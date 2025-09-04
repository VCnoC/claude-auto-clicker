"""
日志管理模块
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = "claude_auto_clicker"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建日志目录在项目内部
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件处理器
        log_file = log_dir / f"{self.name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)


# 全局日志实例
logger = Logger()