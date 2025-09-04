"""
配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .utils.encryption import PasswordEncryption
from .utils.logger import logger


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "target_url": "https://www.aicodemirror.com/dashboard",
        "login": {
            "username": "",
            "password": "",
            "username_selector": "input[name='identifier']",
            "password_selector": "input[name='password']",
            "login_button_selector": "button[type='submit']"
        },
        "click": {
            "button_xpath": "/html/body/div[2]/div/div[4]/main/div/div/div/div[2]/div[2]/div[1]/div[2]/div/div[5]/button",
            "wait_timeout": 20,
            "click_interval": 300  # 5分钟间隔（秒）
        },
        "browser": {
            "headless": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".claude-auto-clicker"
        self.config_file = self.config_dir / "config.json"
        self.encryptor = PasswordEncryption()
        self._ensure_config_dir()
        self._config = None
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self._config is not None:
            return self._config
        
        if not self.config_file.exists():
            logger.info("配置文件不存在，创建默认配置")
            self._config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            return self._config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            # 解密密码
            if self._config.get('login', {}).get('password'):
                encrypted_password = self._config['login']['password']
                try:
                    self._config['login']['password'] = self.encryptor.decrypt(encrypted_password)
                except ValueError as e:
                    logger.error(f"解密密码失败: {e}")
                    self._config['login']['password'] = ""
            
            logger.info("配置加载成功")
            return self._config
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"加载配置失败: {e}")
            self._config = self.DEFAULT_CONFIG.copy()
            return self._config
    
    def save_config(self):
        """保存配置"""
        if self._config is None:
            return
        
        # 创建配置副本用于保存
        config_to_save = self._config.copy()
        
        # 加密密码
        if config_to_save.get('login', {}).get('password'):
            password = config_to_save['login']['password']
            config_to_save['login']['password'] = self.encryptor.encrypt(password)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def set_login_credentials(self, username: str, password: str):
        """设置登录凭据"""
        config = self.load_config()
        config['login']['username'] = username
        config['login']['password'] = password
        self.save_config()
        logger.info("登录凭据已更新")
    
    def get_login_credentials(self) -> tuple[str, str]:
        """获取登录凭据"""
        config = self.load_config()
        username = config.get('login', {}).get('username', '')
        password = config.get('login', {}).get('password', '')
        return username, password
    
    def is_configured(self) -> bool:
        """检查是否已配置登录信息"""
        username, password = self.get_login_credentials()
        return bool(username and password)
    
    def get_config_value(self, key_path: str, default=None):
        """
        获取配置值，支持点号路径
        例如: get_config_value('click.button_xpath')
        """
        config = self.load_config()
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_config_value(self, key_path: str, value):
        """
        设置配置值，支持点号路径
        例如: set_config_value('click.button_xpath', new_xpath)
        """
        config = self.load_config()
        keys = key_path.split('.')
        current = config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值
        current[keys[-1]] = value
        self.save_config()


# 全局配置实例
config_manager = ConfigManager()