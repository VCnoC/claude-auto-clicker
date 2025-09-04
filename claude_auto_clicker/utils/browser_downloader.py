"""
便携式浏览器下载工具

包含：
- ChromiumDownloader：仅管理便携式 Chromium
- BrowserDownloader：同时管理 Chromium 与 ChromeDriver（供 CLI 与运行时优先使用项目内驱动）
"""
import os
import sys
import shutil
import tarfile
import zipfile
import requests
import json
from pathlib import Path
from typing import Optional
from ..utils.logger import logger


class ChromiumDownloader:
    """便携式 Chromium 下载器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.browsers_dir = project_root / "browsers"
        self.chromium_dir = self.browsers_dir / "chromium"
        
        # Chromium 下载 URL 配置（使用已验证可用的版本）
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
    
    def _find_chromium_by_name(self) -> Optional[Path]:
        """按文件名查找 Chromium 可执行文件（不检查权限）"""
        possible_names = ['chrome', 'chromium', 'chromium-browser']
        
        logger.info(f"在目录 {self.chromium_dir} 中按文件名查找 Chromium...")
        
        for root, dirs, files in os.walk(self.chromium_dir):
            for file in files:
                if file in possible_names:
                    file_path = Path(root) / file
                    logger.info(f"✅ 按文件名找到 Chromium: {file_path}")
                    return file_path
        
        logger.error("❌ 未找到任何 Chromium 文件")
        return None
    
    def _find_chromium_executable(self) -> Optional[Path]:
        """在解压后的文件中查找 Chromium 可执行文件"""
        possible_names = ['chrome', 'chromium', 'chromium-browser']
        
        logger.info(f"在目录 {self.chromium_dir} 中查找 Chromium 可执行文件...")
        
        for root, dirs, files in os.walk(self.chromium_dir):
            for file in files:
                if file in possible_names:
                    file_path = Path(root) / file
                    logger.info(f"找到候选文件: {file_path}")
                    
                    # 检查是否可执行
                    if os.access(file_path, os.X_OK):
                        logger.info(f"✅ 找到可执行的 Chromium: {file_path}")
                        return file_path
                    elif file_path.suffix == '.exe':
                        logger.info(f"✅ 找到 Windows 可执行文件: {file_path}")
                        return file_path
                    else:
                        logger.warning(f"⚠️  文件不可执行: {file_path}")
        
        logger.error("❌ 未找到任何 Chromium 可执行文件")
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
        
        # 先按文件名查找，再设置权限
        chromium_exe = self._find_chromium_by_name()
        if not chromium_exe:
            logger.error("未找到 Chromium 可执行文件")
            return False
        
        # 设置可执行权限
        if not self._make_executable(chromium_exe):
            logger.error("设置可执行权限失败")
            return False
        
        logger.info(f"已设置可执行权限: {chromium_exe}")
        
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


class BrowserDownloader:
    """浏览器下载器 - 下载到项目目录（Chromium + ChromeDriver）"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.browsers_dir = project_root / "browsers"
        self.chromium_dir = self.browsers_dir / "chromium"
        self.drivers_dir = self.browsers_dir / "drivers"

        # 确保目录存在
        self.browsers_dir.mkdir(exist_ok=True)
        self.chromium_dir.mkdir(exist_ok=True)
        self.drivers_dir.mkdir(exist_ok=True)

        # Chromium 下载配置（与现有脚本保持一致的稳定版本）
        self.chromium_config = {
            "version": "1108766",
            "urls": {
                "linux": {
                    "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1108766/chrome-linux.zip",
                },
                "windows": {
                    "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/1108766/chrome-win.zip",
                },
                "darwin": {
                    "x64": "https://storage.googleapis.com/chromium-browser-snapshots/Mac/1108766/chrome-mac.zip",
                },
            },
        }

        # ChromeDriver 下载配置（与上述 Chromium 主版本匹配）
        self.driver_config = {
            "version": "110.0.5481.77",
            "urls": {
                "linux": {
                    "x64": "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip",
                },
                "windows": {
                    "x64": "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_win32.zip",
                },
                "darwin": {
                    "x64": "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_mac64.zip",
                },
            },
        }

    def _get_platform_info(self) -> tuple[str, str]:
        platform = sys.platform
        if platform.startswith("linux"):
            platform = "linux"
        elif platform.startswith("win"):
            platform = "windows"
        elif platform.startswith("darwin"):
            platform = "darwin"

        arch = "x64" if sys.maxsize > 2 ** 32 else "x86"
        return platform, arch

    def _download_file(self, url: str, filepath: Path, show_progress: bool = True) -> bool:
        try:
            logger.info(f"开始下载: {url}")
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            response = requests.get(url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="", flush=True)
            if show_progress:
                print()

            logger.info(f"下载完成: {filepath} ({filepath.stat().st_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"下载失败: {e}")
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception:
                    pass
            return False

    def _extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            logger.info(f"开始解压: {zip_path} -> {extract_to}")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"解压完成: {extract_to}")
            return True
        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False

    def _make_executable(self, file_path: Path) -> bool:
        try:
            if sys.platform != "win32":
                os.chmod(file_path, 0o755)
            return True
        except Exception as e:
            logger.error(f"设置可执行权限失败: {e}")
            return False

    def _find_chromium_executable(self) -> Optional[Path]:
        possible_names = ["chrome", "chromium", "chromium-browser", "chrome.exe"]
        for root, _, files in os.walk(self.chromium_dir):
            for file in files:
                if file in possible_names:
                    return Path(root) / file
        return None

    def _find_chromedriver_executable(self) -> Optional[Path]:
        possible_names = ["chromedriver", "chromedriver.exe"]
        for root, _, files in os.walk(self.drivers_dir):
            for file in files:
                if file in possible_names:
                    return Path(root) / file
        return None

    def download_chromium(self) -> bool:
        platform, arch = self._get_platform_info()
        if platform not in self.chromium_config["urls"]:
            logger.error(f"不支持的平台: {platform}")
            return False
        if arch not in self.chromium_config["urls"][platform]:
            logger.error(f"不支持的架构: {arch}")
            return False

        # 清理旧版本
        if self.chromium_dir.exists():
            shutil.rmtree(self.chromium_dir)
            self.chromium_dir.mkdir()

        url = self.chromium_config["urls"][platform][arch]
        zip_path = self.browsers_dir / f"chromium_{platform}_{arch}.zip"

        logger.info(f"下载Chromium for {platform} {arch}...")
        if not self._download_file(url, zip_path):
            return False
        if not self._extract_zip(zip_path, self.chromium_dir):
            return False

        chromium_exe = self._find_chromium_executable()
        if not chromium_exe:
            logger.error("未找到Chromium可执行文件")
            return False
        self._make_executable(chromium_exe)

        try:
            zip_path.unlink()
        except Exception:
            pass
        logger.info(f"✅ Chromium安装成功: {chromium_exe}")
        return True

    def download_chromedriver(self) -> bool:
        platform, arch = self._get_platform_info()
        if platform not in self.driver_config["urls"]:
            logger.error(f"不支持的平台: {platform}")
            return False
        if arch not in self.driver_config["urls"][platform]:
            logger.error(f"不支持的架构: {arch}")
            return False

        # 清理旧版本
        if self.drivers_dir.exists():
            shutil.rmtree(self.drivers_dir)
            self.drivers_dir.mkdir()

        url = self.driver_config["urls"][platform][arch]
        zip_path = self.browsers_dir / f"chromedriver_{platform}_{arch}.zip"

        logger.info(f"下载ChromeDriver for {platform} {arch}...")
        if not self._download_file(url, zip_path):
            return False
        if not self._extract_zip(zip_path, self.drivers_dir):
            return False

        driver_exe = self._find_chromedriver_executable()
        if not driver_exe:
            logger.error("未找到ChromeDriver可执行文件")
            return False
        self._make_executable(driver_exe)

        try:
            zip_path.unlink()
        except Exception:
            pass
        logger.info(f"✅ ChromeDriver安装成功: {driver_exe}")
        return True

    def download_all(self) -> bool:
        logger.info("开始下载浏览器组件...")
        ok = True
        if not self.download_chromium():
            logger.error("Chromium下载失败")
            ok = False
        if not self.download_chromedriver():
            logger.error("ChromeDriver下载失败")
            ok = False
        if ok:
            self._create_version_info()
            logger.info("✅ 所有浏览器组件下载完成")
        else:
            logger.error("❌ 部分组件下载失败")
        return ok

    def _create_version_info(self):
        platform, arch = self._get_platform_info()
        version_info = {
            "chromium_version": self.chromium_config["version"],
            "chromedriver_version": self.driver_config["version"],
            "platform": platform,
            "architecture": arch,
        }
        version_file = self.browsers_dir / "version.json"
        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        logger.info(f"版本信息已保存: {version_file}")

    def is_installed(self) -> bool:
        return self.get_chromium_path() is not None and self.get_chromedriver_path() is not None

    def get_chromium_path(self) -> Optional[Path]:
        return self._find_chromium_executable()

    def get_chromedriver_path(self) -> Optional[Path]:
        return self._find_chromedriver_executable()
