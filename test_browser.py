#!/usr/bin/env python3
"""
测试浏览器检测功能
"""
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_browser_detection():
    """测试浏览器路径检测"""
    try:
        from claude_auto_clicker.core.auto_clicker import AutoClicker
        from claude_auto_clicker.utils.browser_downloader import ChromiumDownloader
        
        print("=" * 50)
        print("🔍 测试便携式 Chromium 下载器")
        print("=" * 50)
        
        downloader = ChromiumDownloader(project_root)
        print(f"项目根目录: {project_root}")
        print(f"浏览器目录: {downloader.browsers_dir}")
        print(f"Chromium 目录: {downloader.chromium_dir}")
        
        if downloader.is_installed():
            path = downloader.get_chromium_path()
            print(f"✅ 便携式 Chromium 已安装: {path}")
        else:
            print("❌ 便携式 Chromium 未安装")
        
        print("\n" + "=" * 50)
        print("🔍 测试 AutoClicker 浏览器检测")
        print("=" * 50)
        
        clicker = AutoClicker()
        chromium_path = clicker._get_chromium_path()
        
        if chromium_path:
            print(f"✅ 找到可用的浏览器: {chromium_path}")
            
            # 测试是否真的可执行
            from pathlib import Path
            import os
            path_obj = Path(chromium_path)
            if path_obj.exists():
                print(f"✅ 文件存在")
                if os.access(path_obj, os.X_OK):
                    print(f"✅ 文件可执行")
                else:
                    print(f"❌ 文件不可执行")
            else:
                print(f"❌ 文件不存在")
        else:
            print("❌ 未找到可用的浏览器")
            
        return chromium_path is not None
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_browser_detection()
    sys.exit(0 if success else 1)