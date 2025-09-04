"""
自动点击核心模块
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import datetime
import os
from pathlib import Path
from typing import Dict, Any

from ..config import config_manager
from ..utils.logger import logger
from .login_handler import LoginHandler


class AutoClicker:
    """自动点击器"""
    
    def __init__(self):
        self.driver = None
        self.config = config_manager.load_config()
        self.login_handler = None
        self.project_root = Path(__file__).parent.parent.parent
    
    def _get_chromium_path(self) -> str:
        """获取 Chromium 浏览器路径，优先使用项目内的版本"""
        # 1. 优先使用便携式 Chromium 下载器查找
        try:
            from ..utils.browser_downloader import ChromiumDownloader
            downloader = ChromiumDownloader(self.project_root)
            portable_path = downloader.get_chromium_path()
            if portable_path and portable_path.exists() and os.access(portable_path, os.X_OK):
                logger.info(f"✅ 找到便携式 Chromium: {portable_path}")
                return str(portable_path)
        except Exception as e:
            logger.debug(f"便携式 Chromium 检测失败: {e}")
        
        # 2. 手动检查项目内的常见路径
        local_chromium_paths = [
            self.project_root / "browsers" / "chromium" / "chrome-linux" / "chrome",
            self.project_root / "browsers" / "chromium" / "chrome-win" / "chrome.exe",
            self.project_root / "browsers" / "chromium" / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium",
            self.project_root / "browsers" / "chromium" / "chrome",
            self.project_root / "chromium" / "chrome"
        ]
        
        for path in local_chromium_paths:
            if path.exists() and os.access(path, os.X_OK):
                logger.info(f"✅ 找到项目内 Chromium: {path}")
                return str(path)
        
        # 3. 检查系统安装的 Chromium
        system_chromium_paths = [
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "/opt/google/chrome/chrome"
        ]
        
        for path in system_chromium_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                logger.info(f"✅ 找到系统 Chromium: {path}")
                return path
        
        logger.warning("❌ 未找到可用的 Chromium 浏览器")
        return None
    
    def _setup_browser(self) -> webdriver.Chrome:
        """设置浏览器"""
        options = webdriver.ChromeOptions()
        
        # 从配置读取浏览器设置
        browser_config = self.config.get('browser', {})
        
        if browser_config.get('headless', False):
            options.add_argument("--headless")
        
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")  # 解决共享内存问题
        
        user_agent = browser_config.get('user_agent')
        if user_agent:
            options.add_argument(f"user-agent='{user_agent}'")
        
        # 获取 Chromium 路径
        chromium_path = self._get_chromium_path()
        
        if chromium_path:
            # 尝试启动 Chromium
            try:
                logger.info("尝试启动 Chromium...")
                # 创建新的选项实例避免冲突
                chromium_options = webdriver.ChromeOptions()
                for arg in options.arguments:
                    chromium_options.add_argument(arg)
                chromium_options.binary_location = chromium_path
                
                # 添加兼容性选项（特别针对老版本 Chromium）
                chromium_options.add_argument("--disable-extensions")
                chromium_options.add_argument("--disable-plugins")
                chromium_options.add_argument("--disable-dev-shm-usage")
                chromium_options.add_argument("--disable-gpu")
                chromium_options.add_argument("--no-first-run")
                chromium_options.add_argument("--disable-default-apps")
                chromium_options.add_argument("--disable-background-timer-throttling")
                chromium_options.add_argument("--disable-renderer-backgrounding")
                chromium_options.add_argument("--disable-backgrounding-occluded-windows")
                chromium_options.add_argument("--disable-blink-features=AutomationControlled")
                chromium_options.add_argument("--disable-web-security")
                chromium_options.add_argument("--allow-running-insecure-content")
                chromium_options.add_argument("--ignore-certificate-errors")
                chromium_options.add_argument("--ignore-ssl-errors")
                chromium_options.add_argument("--ignore-certificate-errors-spki-list")
                
                # 清除 webdriver 相关环境变量（避免检测）
                chromium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chromium_options.add_experimental_option('useAutomationExtension', False)
                
                # 使用简单的 ChromeDriverManager
                logger.info("使用默认 ChromeDriverManager 获取 ChromeDriver...")
                service = Service(ChromeDriverManager().install())
                
                driver = webdriver.Chrome(service=service, options=chromium_options)
                logger.info("✅ Chromium 启动成功")
                return driver
            except Exception as e:
                logger.info(f"Chromium 启动失败: {e}")
                logger.info("尝试回退到系统默认浏览器...")
        
        # 回退到系统默认 Chrome/Chromium
        try:
            logger.info("尝试使用系统默认浏览器...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ 系统浏览器启动成功")
            return driver
        except Exception as e:
            logger.error(f"系统浏览器启动失败: {e}")
            raise Exception(
                "❌ 无法启动浏览器。建议:\n"
                f"• 运行 './claude-auto-clicker install-chromium' 下载便携版 Chromium\n"
                "• 或安装系统 Chromium: sudo apt install chromium-browser"
            )
    
    def _handle_login_if_needed(self) -> bool:
        """处理登录（如果需要）"""
        if self.login_handler.check_if_login_required():
            logger.info("检测到需要登录，开始自动登录...")
            
            username, password = config_manager.get_login_credentials()
            if not username or not password:
                logger.error("未配置登录凭据，请先运行 'claude-auto-clicker login' 命令")
                return False
            
            login_selectors = self.config.get('login', {})
            login_success = self.login_handler.perform_login(username, password, login_selectors)
            
            if not login_success:
                logger.error("自动登录失败")
                return False
            
            # 登录成功后重新打开目标页面
            target_url = self.config.get('target_url')
            self.driver.get(target_url)
            logger.info("登录成功，重新打开目标页面")
        
        return True
    
    def _perform_click(self) -> bool:
        """执行点击操作"""
        try:
            click_config = self.config.get('click', {})
            wait_timeout = click_config.get('wait_timeout', 20)
            button_xpath = click_config.get('button_xpath')
            
            if not button_xpath:
                logger.error("未配置按钮XPath")
                return False
            
            # 等待按钮可点击
            wait = WebDriverWait(self.driver, wait_timeout)
            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            logger.info("成功定位到按钮")
            
            # 执行点击
            button.click()
            logger.info("按钮点击成功！")
            
            # 等待响应
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"点击操作失败: {e}")
            return False
    
    def perform_single_click(self) -> bool:
        """执行单次点击任务"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{current_time}] 开始执行单次点击任务...")
        
        try:
            # 设置浏览器
            self.driver = self._setup_browser()
            self.login_handler = LoginHandler(self.driver)
            
            # 打开目标网页
            target_url = self.config.get('target_url')
            self.driver.get(target_url)
            logger.info(f"成功打开网页: {target_url}")
            
            # 处理登录
            if not self._handle_login_if_needed():
                return False
            
            # 执行点击
            success = self._perform_click()
            return success
            
        except Exception as e:
            logger.error(f"执行过程中发生错误: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器已关闭")
    
    def start_continuous_clicking(self, interval_seconds: int = None):
        """开始连续点击模式"""
        if interval_seconds is None:
            interval_seconds = self.config.get('click', {}).get('click_interval', 300)
        
        logger.info(f"开始连续点击模式，间隔 {interval_seconds} 秒")
        
        while True:
            try:
                success = self.perform_single_click()
                if success:
                    logger.info(f"点击成功，等待 {interval_seconds} 秒后继续")
                else:
                    logger.warning(f"点击失败，等待 {interval_seconds} 秒后重试")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("接收到中断信号，停止连续点击")
                break
            except Exception as e:
                logger.error(f"连续点击过程中出错: {e}")
                time.sleep(interval_seconds)


# 全局实例
auto_clicker = AutoClicker()