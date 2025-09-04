#!/usr/bin/env python3
"""
调试 Chromium 启动问题
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chromium_launch():
    """测试 Chromium 启动"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("=" * 60)
        print("🔍 调试 Chromium 启动问题")
        print("=" * 60)
        
        # 便携式 Chromium 路径
        chromium_path = "/home/vc/claude-auto-clicker/browsers/chromium/chrome-linux/chrome"
        
        # 检查文件是否存在
        if not Path(chromium_path).exists():
            print(f"❌ Chromium 文件不存在: {chromium_path}")
            return False
        
        print(f"✅ Chromium 路径验证: {chromium_path}")
        
        # 测试基本的 ChromeDriver 获取
        print("\n🔧 获取 ChromeDriver...")
        try:
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver 路径: {driver_path}")
        except Exception as e:
            print(f"❌ ChromeDriver 获取失败: {e}")
            return False
        
        # 测试最小化配置的 Chromium 启动
        print("\n🚀 尝试启动 Chromium（最小化配置）...")
        
        options = webdriver.ChromeOptions()
        options.binary_location = chromium_path
        
        # 最基本的选项
        options.add_argument("--headless")  # 无界面模式，降低复杂度
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # 额外的兼容性选项
        options.add_argument("--remote-debugging-port=0")  # 自动分配端口
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        try:
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ Chromium 启动成功！")
            
            # 简单测试
            print("📄 测试页面加载...")
            driver.get("data:text/html,<html><body><h1>Test Page</h1></body></html>")
            title = driver.title
            print(f"✅ 页面加载成功: {title}")
            
            driver.quit()
            print("✅ Chromium 正常关闭")
            return True
            
        except Exception as e:
            print(f"❌ Chromium 启动失败: {e}")
            print(f"错误类型: {type(e).__name__}")
            
            # 提供详细的错误信息
            if "Bad Gateway" in str(e):
                print("\n💡 Bad Gateway 错误通常表示:")
                print("   1. ChromeDriver 与 Chromium 版本不兼容")
                print("   2. 端口冲突或网络问题")
                print("   3. Chromium 启动参数不正确")
            
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_system_info():
    """检查系统信息"""
    import subprocess
    print("\n" + "=" * 60)
    print("🖥️  系统信息")
    print("=" * 60)
    
    # Chromium 版本
    try:
        result = subprocess.run([
            "/home/vc/claude-auto-clicker/browsers/chromium/chrome-linux/chrome", 
            "--version"
        ], capture_output=True, text=True, timeout=10)
        print(f"Chromium 版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"无法获取 Chromium 版本: {e}")
    
    # Python 版本
    print(f"Python 版本: {sys.version}")
    
    # Selenium 版本
    try:
        import selenium
        print(f"Selenium 版本: {selenium.__version__}")
    except:
        print("无法获取 Selenium 版本")

if __name__ == "__main__":
    check_system_info()
    success = test_chromium_launch()
    
    print("\n" + "=" * 60)
    print("📋 测试结果")
    print("=" * 60)
    print(f"{'🎉 测试成功' if success else '❌ 测试失败'}")
    
    if not success:
        print("\n💡 建议:")
        print("1. 检查 Chromium 是否可以手动启动")
        print("2. 尝试更新 selenium 和 webdriver-manager")
        print("3. 检查是否有端口冲突")
    
    sys.exit(0 if success else 1)