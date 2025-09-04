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
        
        # 优先尝试 Chromium（推荐用于自动化）
        try:
            logger.info("尝试启动 Chromium...")
            options.binary_location = "/usr/bin/chromium-browser"
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ Chromium 启动成功（推荐用于自动化）")
            return driver
        except Exception as e:
            logger.info(f"Chromium 启动失败: {e}")
            logger.info("尝试使用 Chrome...")
            
            # 回退到 Chrome
            options.binary_location = None  # 重置二进制位置
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ Chrome 启动成功")
                return driver
            except Exception as e2:
                logger.error(f"Chrome 也启动失败: {e2}")
                raise Exception(
                    "❌ 无法启动浏览器。请安装 Chromium（推荐）或 Chrome:\n"
                    "• Chromium: sudo apt install chromium-browser\n"
                    "• Chrome: sudo apt install google-chrome-stable"
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