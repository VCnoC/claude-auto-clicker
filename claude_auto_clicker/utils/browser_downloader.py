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
        
        # Chromium 下载 URL 配置（使用稳定版本）
        self.chromium_urls = {
            "linux": {
                "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1108766/chrome-linux.zip",
            },
            "windows": {
                "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/1108766/chrome-win.zip",
            },
            "darwin": {  # macOS
                "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Mac/1108766/chrome-mac.zip"
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
            
            # 添加用户代理和其他头部
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            logger.info(f"下载内容类型: {content_type}")
            
            # 如果是 HTML 页面，说明可能是重定向错误
            if 'text/html' in content_type:
                logger.error(f"下载的是 HTML 页面而不是文件，URL 可能有问题: {url}")
                return False
            
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
            
            # 验证下载的文件大小
            if filepath.stat().st_size < 1024:  # 小于 1KB 可能是错误页面
                logger.error(f"下载的文件太小 ({filepath.stat().st_size} bytes)，可能下载失败")
                if filepath.exists():
                    filepath.unlink()
                return False
            
            logger.info(f"下载完成: {filepath} ({filepath.stat().st_size} bytes)")
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
            logger.info(f"开始解压: {archive_path} -> {extract_to}")
            
            # 检查文件头部来确定实际文件类型
            with open(archive_path, 'rb') as f:
                header = f.read(10)
            
            # ZIP 文件魔术数字
            if header[:2] == b'PK':
                logger.info("检测到 ZIP 文件")
                try:
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_to)
                    logger.info(f"ZIP 解压完成: {extract_to}")
                    return True
                except zipfile.BadZipFile as e:
                    logger.error(f"ZIP 文件损坏: {e}")
                    return False
            
            # TAR/GZIP 文件魔术数字
            elif header[:2] == b'\x1f\x8b':  # GZIP
                logger.info("检测到 GZIP 文件")
                try:
                    with tarfile.open(archive_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(extract_to)
                    logger.info(f"GZIP 解压完成: {extract_to}")
                    return True
                except tarfile.ReadError as e:
                    logger.error(f"GZIP 文件处理失败: {e}")
                    return False
            
            # 纯 TAR 文件
            elif header[:5] == b'ustar':
                logger.info("检测到 TAR 文件")
                try:
                    with tarfile.open(archive_path, 'r:') as tar_ref:
                        tar_ref.extractall(extract_to)
                    logger.info(f"TAR 解压完成: {extract_to}")
                    return True
                except tarfile.ReadError as e:
                    logger.error(f"TAR 文件处理失败: {e}")
                    return False
            
            else:
                # 尝试读取更多内容来判断
                logger.warning(f"无法识别文件类型，文件头: {header}")
                
                # 先检查文件内容是否是 HTML（错误页面）
                with open(archive_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_start = f.read(200)
                    if content_start.strip().startswith('<!DOCTYPE') or '<html' in content_start:
                        logger.error("下载的是 HTML 页面，不是压缩包文件")
                        return False
                
                # 强制按扩展名尝试解压
                if archive_path.suffix == '.zip':
                    logger.info("根据扩展名强制尝试 ZIP 解压")
                    try:
                        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_to)
                        logger.info(f"强制 ZIP 解压成功: {extract_to}")
                        return True
                    except Exception as e:
                        logger.error(f"强制 ZIP 解压失败: {e}")
                
                logger.error(f"无法处理的文件格式: {archive_path}")
                return False
            
        except Exception as e:
            logger.error(f"解压过程中出现异常: {e}")
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
        
        # 所有平台都使用 .zip 格式
        archive_path = self.browsers_dir / f"chromium_{platform}_{arch}.zip"
        
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