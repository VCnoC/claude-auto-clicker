#!/usr/bin/env python3
"""
简单的浏览器路径检测测试
"""
from pathlib import Path
import sys
import os

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_manual_detection():
    """手动测试浏览器路径检测逻辑"""
    print("=" * 60)
    print("🔍 手动测试浏览器路径检测")
    print("=" * 60)
    
    # 检查便携式 Chromium 路径
    portable_paths = [
        project_root / "browsers" / "chromium" / "chrome-linux" / "chrome",
        project_root / "browsers" / "chromium" / "chrome-win" / "chrome.exe",
        project_root / "browsers" / "chromium" / "chrome",
    ]
    
    print("📁 检查便携式 Chromium:")
    for path in portable_paths:
        if path.exists():
            executable = os.access(path, os.X_OK) if os.name != 'nt' else path.suffix == '.exe'
            status = "✅ 可执行" if executable else "❌ 不可执行"
            print(f"  {status}: {path}")
            if executable:
                return str(path)
        else:
            print(f"  ❌ 不存在: {path}")
    
    # 检查系统 Chromium
    system_paths = [
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium",
        "/opt/google/chrome/chrome"
    ]
    
    print("\n🖥️  检查系统 Chromium:")
    for path_str in system_paths:
        path = Path(path_str)
        if path.exists():
            executable = os.access(path, os.X_OK)
            status = "✅ 可执行" if executable else "❌ 不可执行"
            print(f"  {status}: {path}")
            if executable:
                return str(path)
        else:
            print(f"  ❌ 不存在: {path}")
    
    print("\n❌ 未找到任何可用的浏览器")
    return None

def test_downloader_logic():
    """测试下载器逻辑"""
    print("\n" + "=" * 60)
    print("🔍 测试下载器查找逻辑")
    print("=" * 60)
    
    try:
        from claude_auto_clicker.utils.browser_downloader import ChromiumDownloader
        
        downloader = ChromiumDownloader(project_root)
        print(f"项目根目录: {downloader.project_root}")
        print(f"浏览器目录: {downloader.browsers_dir}")
        print(f"Chromium 目录: {downloader.chromium_dir}")
        
        # 测试按名称查找
        found_by_name = downloader._find_chromium_by_name()
        if found_by_name:
            print(f"✅ 按名称找到: {found_by_name}")
            executable = os.access(found_by_name, os.X_OK)
            print(f"{'✅ 可执行' if executable else '❌ 不可执行'}")
            return str(found_by_name) if executable else None
        else:
            print("❌ 按名称未找到")
        
        # 测试可执行文件查找
        found_executable = downloader._find_chromium_executable()
        if found_executable:
            print(f"✅ 找到可执行文件: {found_executable}")
            return str(found_executable)
        else:
            print("❌ 未找到可执行文件")
            
        return None
        
    except Exception as e:
        print(f"❌ 下载器测试失败: {e}")
        return None

if __name__ == "__main__":
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {project_root}")
    
    # 手动检测
    manual_result = test_manual_detection()
    
    # 下载器检测
    downloader_result = test_downloader_logic()
    
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    if manual_result:
        print(f"✅ 手动检测成功: {manual_result}")
    else:
        print("❌ 手动检测失败")
    
    if downloader_result:
        print(f"✅ 下载器检测成功: {downloader_result}")
    else:
        print("❌ 下载器检测失败")
    
    success = manual_result or downloader_result
    print(f"\n{'🎉 测试成功' if success else '❌ 测试失败'}")
    
    sys.exit(0 if success else 1)