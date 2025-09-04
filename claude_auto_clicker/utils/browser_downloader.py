"""
便携式 Chromium 浏览器下载工具
"""
import os
import sys
import shutil
import tarfile
import zipfile
import requests
from pathlib import Path
from typing import Optional
from ..utils.logger import logger


class ChromiumDownloader:
    """便携式 Chromium 下载器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.browsers_dir = project_root / "browsers"
        self.chromium_dir = self.browsers_dir / "chromium"
        
        # Chromium 下载 URL 配置
        self.chromium_urls = {
            "linux": {
                "x64": "https://download-chromium.appspot.com/dl/Linux_x64?type=snapshots",
                "x86": "https://download-chromium.appspot.com/dl/Linux?type=snapshots"
            },
            "windows": {
                "x64": "https://download-chromium.appspot.com/dl/Win_x64?type=snapshots",
                "x86": "https://download-chromium.appspot.com/dl/Win?type=snapshots"
            },
            "darwin": {  # macOS
                "x64": "https://download-chromium.appspot.com/dl/Mac?type=snapshots"
            }
        }
    
    def _get_platform_info(self) -> tuple[str, str]:
        """获取平台和架构信息"""
        platform = sys.platform
        if platform.startswith('linux'):
            platform = 'linux'
        elif platform.startswith('win'):
            platform = 'windows'
        elif platform.startswith('darwin'):
            platform = 'darwin'
        
        # 检测架构
        arch = 'x64' if sys.maxsize > 2**32 else 'x86'
        
        return platform, arch
    
    def _download_file(self, url: str, filepath: Path, show_progress: bool = True) -> bool:
        """下载文件"""
        try:
            logger.info(f"开始下载: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if show_progress and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            if show_progress:
                print()  # 换行
            
            logger.info(f"下载完成: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"下载失败: {e}")
            if filepath.exists():
                filepath.unlink()
            return False
    
    def _extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """解压归档文件"""
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.gz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                logger.error(f"不支持的归档格式: {archive_path.suffix}")
                return False
            
            logger.info(f"解压完成: {extract_to}")
            return True
            
        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False
    
    def _make_executable(self, file_path: Path) -> bool:
        """设置文件为可执行"""
        try:
            if sys.platform != 'win32':
                os.chmod(file_path, 0o755)
            return True
        except Exception as e:
            logger.error(f"设置可执行权限失败: {e}")
            return False
    
    def _find_chromium_executable(self) -> Optional[Path]:
        """在解压后的文件中查找 Chromium 可执行文件"""
        possible_names = ['chrome', 'chromium', 'chromium-browser']
        
        for root, dirs, files in os.walk(self.chromium_dir):
            for file in files:
                if file in possible_names or file.startswith('chrome'):
                    file_path = Path(root) / file
                    if os.access(file_path, os.X_OK) or file_path.suffix == '.exe':
                        return file_path
        
        return None
    
    def download_and_install(self) -> bool:
        """下载并安装便携式 Chromium"""
        platform, arch = self._get_platform_info()
        
        if platform not in self.chromium_urls:
            logger.error(f"不支持的平台: {platform}")
            return False
        
        if arch not in self.chromium_urls[platform]:
            logger.error(f"不支持的架构: {arch}")
            return False
        
        # 创建目录
        self.browsers_dir.mkdir(exist_ok=True)
        
        # 如果已经存在，询问是否重新下载
        if self.chromium_dir.exists():
            logger.info("检测到已存在的 Chromium，将重新下载...")
            shutil.rmtree(self.chromium_dir)
        
        # 下载 URL
        download_url = self.chromium_urls[platform][arch]
        
        # 确定下载文件名
        archive_extension = '.zip' if platform == 'windows' else '.tar.gz'
        archive_path = self.browsers_dir / f"chromium_{platform}_{arch}{archive_extension}"
        
        # 下载文件
        logger.info(f"为 {platform} {arch} 下载 Chromium...")
        if not self._download_file(download_url, archive_path):
            return False
        
        # 解压文件
        logger.info("解压 Chromium...")
        if not self._extract_archive(archive_path, self.chromium_dir):
            return False
        
        # 查找可执行文件
        chromium_exe = self._find_chromium_executable()
        if not chromium_exe:
            logger.error("未找到 Chromium 可执行文件")
            return False
        
        # 设置可执行权限
        self._make_executable(chromium_exe)
        
        # 清理下载的归档文件
        archive_path.unlink()
        
        logger.info(f"✅ Chromium 安装成功: {chromium_exe}")
        return True
    
    def is_installed(self) -> bool:
        """检查 Chromium 是否已安装"""
        return self._find_chromium_executable() is not None
    
    def get_chromium_path(self) -> Optional[Path]:
        """获取 Chromium 可执行文件路径"""
        return self._find_chromium_executable()
    
    def uninstall(self) -> bool:
        """卸载便携式 Chromium"""
        if self.chromium_dir.exists():
            try:
                shutil.rmtree(self.chromium_dir)
                logger.info("✅ 便携式 Chromium 已卸载")
                return True
            except Exception as e:
                logger.error(f"卸载失败: {e}")
                return False
        else:
            logger.info("便携式 Chromium 未安装")
            return True