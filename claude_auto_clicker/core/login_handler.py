"""
登录处理模块
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Tuple

from ..utils.logger import logger


class LoginHandler:
    """登录处理器"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def check_if_login_required(self) -> bool:
        """
        检测当前页面是否需要登录
        返回 True 如果需要登录，False 如果不需要
        """
        try:
            # 检测常见的登录页面标识
            login_indicators = [
                "input[name='identifier']",
                "input[name='email']", 
                "input[type='email']",
                "input[name='password']",
                "input[type='password']",
                "button[type='submit']",
                ".login-form",
                "#login",
                ".signin"
            ]
            
            for indicator in login_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        logger.info("检测到登录页面")
                        return True
                except:
                    continue
                    
            # 检查URL是否包含登录相关关键词
            current_url = self.driver.current_url.lower()
            login_keywords = ["login", "signin", "auth", "sign-in"]
            for keyword in login_keywords:
                if keyword in current_url:
                    logger.info(f"URL包含登录关键词: {keyword}")
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"检测登录状态时出错: {e}")
            return False
    
    def perform_login(self, username: str, password: str, selectors: dict) -> bool:
        """
        执行自动登录操作
        :param username: 用户名
        :param password: 密码
        :param selectors: 选择器配置
        :return: 登录是否成功
        """
        try:
            logger.info("开始执行自动登录...")
            
            # 等待并输入用户名
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors["username_selector"]))
            )
            username_field.clear()
            username_field.send_keys(username)
            logger.info("用户名输入完成")
            
            # 等待并输入密码
            password_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors["password_selector"]))
            )
            password_field.clear()
            password_field.send_keys(password)
            logger.info("密码输入完成")
            
            # 点击登录按钮
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["login_button_selector"]))
            )
            login_button.click()
            logger.info("登录按钮点击完成")
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                logger.info("登录成功！")
                return True
            else:
                logger.warning("登录可能失败，请检查账号密码")
                return False
                
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False