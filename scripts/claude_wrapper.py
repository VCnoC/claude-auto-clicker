#!/usr/bin/env python3
"""
Claude 命令包装器
用于拦截 claude 命令并在启动 claude code 时同时启动自动点击功能
"""
import sys
import os
import subprocess
import threading
import time
import signal
from pathlib import Path

# 添加自动点击工具到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_auto_clicker.core.auto_clicker import auto_clicker
from claude_auto_clicker.config import config_manager
from claude_auto_clicker.utils.logger import logger


class ClaudeWrapper:
    """Claude 命令包装器"""
    
    def __init__(self):
        self.auto_click_thread = None
        self.claude_process = None
        self.should_stop = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，正在清理...")
        self.should_stop = True
        if self.claude_process:
            self.claude_process.terminate()
        sys.exit(0)
    
    def _find_original_claude(self) -> str:
        """查找原始的 claude 命令"""
        # 获取当前脚本路径
        current_script = os.path.abspath(__file__)
        
        # 在 PATH 中查找 claude 命令，排除当前包装器
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for path_dir in path_dirs:
            claude_path = os.path.join(path_dir, 'claude')
            if (os.path.exists(claude_path) and 
                os.access(claude_path, os.X_OK) and 
                os.path.abspath(claude_path) != current_script):
                
                # 检查是否是真正的 claude 命令（而不是我们的包装器）
                try:
                    result = subprocess.run([claude_path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if 'Claude Code' in result.stdout or 'claude' in result.stdout.lower():
                        return claude_path
                except:
                    continue
        
        # 如果找不到，尝试默认位置
        default_paths = [
            '/usr/local/bin/claude',
            os.path.expanduser('~/.local/bin/claude'),
            '/opt/claude/bin/claude'
        ]
        
        for path in default_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        raise FileNotFoundError("无法找到原始的 claude 命令")
    
    def _should_start_auto_click(self, args: list) -> bool:
        """判断是否应该启动自动点击功能"""
        # 检查是否启动 claude code
        if not args:
            return False
            
        # 检查命令参数
        for arg in args:
            if arg.lower() in ['code', '--code', 'code-editor']:
                return True
        
        # 如果没有参数或参数是帮助相关，可能是启动 code
        if len(args) == 0 or args[0] in ['--help', '-h']:
            return False
            
        return True  # 默认认为是启动 code
    
    def _auto_click_worker(self):
        """自动点击工作线程"""
        if not config_manager.is_configured():
            logger.warning("未配置登录凭据，跳过自动点击功能")
            return
        
        # 等待一段时间让 claude code 启动
        time.sleep(10)
        
        interval = config_manager.get_config_value('click.click_interval', 300)
        logger.info(f"开始后台自动点击，间隔 {interval} 秒")
        
        while not self.should_stop:
            try:
                success = auto_clicker.perform_single_click()
                if success:
                    logger.info(f"后台点击成功，等待 {interval} 秒")
                else:
                    logger.warning(f"后台点击失败，等待 {interval} 秒后重试")
                
                # 分段睡眠，便于响应停止信号
                for _ in range(interval):
                    if self.should_stop:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"自动点击过程中出错: {e}")
                time.sleep(30)  # 出错后等待30秒
    
    def run(self, args: list):
        """运行 claude 命令"""
        try:
            # 查找原始 claude 命令
            original_claude = self._find_original_claude()
            
            # 判断是否需要启动自动点击
            should_auto_click = self._should_start_auto_click(args)
            
            if should_auto_click:
                logger.info("检测到 claude code 启动，准备启动后台自动点击")
                
                # 启动自动点击线程
                self.auto_click_thread = threading.Thread(
                    target=self._auto_click_worker, 
                    daemon=True
                )
                self.auto_click_thread.start()
            
            # 启动原始 claude 命令
            logger.info(f"启动原始 claude 命令: {original_claude} {' '.join(args)}")
            self.claude_process = subprocess.Popen([original_claude] + args)
            
            # 等待 claude 命令完成
            self.claude_process.wait()
            
        except FileNotFoundError:
            print("❌ 无法找到原始的 claude 命令")
            print("请确保已正确安装 Claude Code")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("接收到中断信号")
        except Exception as e:
            logger.error(f"运行 claude 命令时出错: {e}")
            sys.exit(1)
        finally:
            self.should_stop = True


def main():
    """主入口函数"""
    wrapper = ClaudeWrapper()
    wrapper.run(sys.argv[1:])


if __name__ == "__main__":
    main()