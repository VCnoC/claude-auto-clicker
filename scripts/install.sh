#!/bin/bash
# Claude Auto Clicker 安装脚本 (Linux/Mac)

set -e

echo "🚀 开始安装 Claude Auto Clicker..."

# 检查 Python 版本
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.7"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo "❌ 错误: 需要 Python $required_version 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python 版本检查通过: $python_version"

# 检查是否已安装 Claude Code
if ! command -v claude &> /dev/null; then
    echo "❌ 错误: 未找到 claude 命令"
    echo "请先安装 Claude Code: https://claude.ai/code"
    exit 1
fi

echo "✅ 检测到 Claude Code"

# 检查并安装浏览器
check_and_install_browser() {
    echo "🌐 检查浏览器环境..."
    
    # 优先检查 Chromium（推荐用于自动化）
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium 已安装（推荐用于自动化）"
        return 0
    fi
    
    # 检查 Chrome
    if command -v google-chrome &> /dev/null; then
        echo "✅ Google Chrome 已安装"
        return 0
    fi
    
    # 都没有，推荐安装 Chromium
    echo "⚠️  未检测到浏览器"
    echo "💡 推荐安装 Chromium（轻量级，适合自动化任务）"
    
    if command -v apt &> /dev/null; then
        read -p "是否安装 Chromium 浏览器？[推荐] (Y/n): " install_browser
        # 默认为 Y
        if [[ $install_browser =~ ^[Nn]$ ]]; then
            echo "⏭️  跳过浏览器安装"
        else
            echo "📦 正在安装 Chromium（轻量级浏览器）..."
            echo "💭 Chromium 优势：轻量、开源、适合自动化"
            
            if sudo apt update && sudo apt install -y chromium-browser; then
                echo "✅ Chromium 安装成功！"
                echo "📏 安装大小：约 80MB"
                return 0
            else
                echo "❌ Chromium 自动安装失败"
                echo "🔧 请手动安装: sudo apt install chromium-browser"
            fi
        fi
    fi
    
    echo ""
    echo "📖 浏览器安装指南："
    echo "   • Chromium（推荐）: sudo apt install chromium-browser"
    echo "   • Chrome（完整版）: sudo apt install google-chrome-stable"
    echo ""
    echo "ℹ️  继续安装，但运行时需要浏览器支持"
}

# 检查浏览器
check_and_install_browser

# 检查并安装 python3-venv（如果需要）
check_and_install_venv() {
    if ! python3 -m venv --help &> /dev/null; then
        echo "⚠️  检测到系统缺少 python3-venv 模块"
        
        # 检查是否为 Ubuntu/Debian 系统
        if command -v apt &> /dev/null; then
            echo "🔧 正在自动安装 python3-venv..."
            
            # 获取 Python 版本
            python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            
            # 尝试自动安装
            if sudo apt update && sudo apt install -y python3-venv python${python_version}-venv; then
                echo "✅ python3-venv 安装成功"
                return 0
            else
                echo "❌ 自动安装失败"
                echo "请手动运行: sudo apt install python3-venv"
                exit 1
            fi
        else
            echo "❌ 不支持的系统类型，请手动安装 python3-venv"
            echo "Ubuntu/Debian: sudo apt install python3-venv"
            echo "CentOS/RHEL: sudo yum install python3-venv"
            echo "Fedora: sudo dnf install python3-venv"
            exit 1
        fi
    fi
}

# 创建本地虚拟环境（推荐）
read -p "是否要创建本地虚拟环境？(y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 创建本地虚拟环境..."
    
    # 检查并安装 venv 支持
    check_and_install_venv
    
    # 在项目目录内创建虚拟环境
    if python3 -m venv ./venv; then
        source ./venv/bin/activate
        echo "✅ 本地虚拟环境已创建并激活"
        echo "📁 虚拟环境位置: $(pwd)/venv"
        
        # 记录虚拟环境路径
        echo "export CLAUDE_AUTO_CLICKER_VENV=$(pwd)/venv" > .env
        echo "✅ 环境变量已保存到 .env 文件"
    else
        echo "❌ 虚拟环境创建失败"
        echo "继续使用系统环境安装..."
    fi
else
    echo "⚠️  将使用系统 Python 环境"
fi

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 本地开发模式安装（不安装到系统）
echo "📦 配置 Claude Auto Clicker 本地运行环境..."

# 创建启动脚本
cat > claude-auto-clicker << 'EOF'
#!/bin/bash
# Claude Auto Clicker 本地启动脚本

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境（如果存在）
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
    if [ -d "$CLAUDE_AUTO_CLICKER_VENV" ]; then
        source "$CLAUDE_AUTO_CLICKER_VENV/bin/activate"
    fi
elif [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# 添加项目路径到 Python 路径
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# 运行 CLI（避免模块导入警告）
python -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from claude_auto_clicker.cli import main
if __name__ == '__main__':
    main()
" "$@"
EOF

chmod +x claude-auto-clicker
echo "✅ 本地启动脚本已创建"

# 备份原始 claude 命令
claude_path=$(which claude)
if [ -f "$claude_path" ] && [ ! -f "${claude_path}.original" ]; then
    echo "💾 备份原始 claude 命令..."
    sudo cp "$claude_path" "${claude_path}.original"
fi

# 创建并安装 Claude 包装器
wrapper_script="claude_wrapper_local.py"
cat > "$wrapper_script" << 'EOF'
#!/usr/bin/env python3
"""本地版本的 Claude 命令包装器"""
import sys
import os
from pathlib import Path

# 获取当前脚本所在目录（项目根目录）
PROJECT_ROOT = Path(__file__).parent.absolute()

# 添加项目路径到 Python 路径
sys.path.insert(0, str(PROJECT_ROOT))

# 激活虚拟环境（如果存在）
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.startswith("export CLAUDE_AUTO_CLICKER_VENV="):
                venv_path = line.split("=", 1)[1].strip()
                venv_python = Path(venv_path) / "bin" / "python"
                if venv_python.exists():
                    os.execv(str(venv_python), [str(venv_python)] + [__file__] + sys.argv[1:])

# 如果没有虚拟环境，检查本地 venv
local_venv = PROJECT_ROOT / "venv" / "bin" / "python"
if local_venv.exists() and str(local_venv) not in sys.executable:
    os.execv(str(local_venv), [str(local_venv)] + [__file__] + sys.argv[1:])

# 导入包装器逻辑
from scripts.claude_wrapper import main

if __name__ == "__main__":
    # 设置项目根目录环境变量
    os.environ["CLAUDE_AUTO_CLICKER_ROOT"] = str(PROJECT_ROOT)
    main()
EOF

echo "🔧 安装 claude 命令包装器..."
sudo cp "$wrapper_script" "$claude_path"
sudo chmod +x "$claude_path"
echo "✅ 本地包装器安装完成"

# 创建本地卸载脚本
cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️  卸载 Claude Auto Clicker..."

# 获取当前目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 恢复原始 claude 命令
claude_path=$(which claude 2>/dev/null)
if [ -f "${claude_path}.original" ]; then
    echo "🔄 恢复原始 claude 命令..."
    sudo mv "${claude_path}.original" "$claude_path"
    echo "✅ 已恢复原始 claude 命令"
else
    echo "⚠️  未找到原始 claude 命令备份"
fi

# 询问是否删除 Chromium
echo ""
echo "🌐 Chromium 浏览器处理："
if command -v chromium-browser &> /dev/null; then
    echo "检测到已安装的 Chromium 浏览器"
    read -p "是否也删除 Chromium 浏览器？(y/n): " remove_chromium
    if [[ $remove_chromium =~ ^[Yy]$ ]]; then
        echo "🗑️  正在删除 Chromium..."
        if sudo apt remove -y chromium-browser; then
            echo "✅ Chromium 已删除"
        else
            echo "❌ Chromium 删除失败，请手动执行: sudo apt remove chromium-browser"
        fi
    else
        echo "⏭️  保留 Chromium 浏览器（其他程序可能需要）"
    fi
else
    echo "ℹ️  未检测到 Chromium 浏览器"
fi

# 清理 webdriver-manager 缓存
echo ""
echo "🧹 清理驱动缓存..."
if [ -d "$HOME/.wdm" ]; then
    rm -rf "$HOME/.wdm"
    echo "✅ 已清理 webdriver-manager 缓存"
fi

# 删除项目文件夹提醒
echo ""
echo "📁 项目文件夹："
echo "   $PROJECT_DIR"
echo ""
echo "要完全删除 Claude Auto Clicker，请："
echo "1. 退出当前目录: cd .."
echo "2. 删除整个项目文件夹: rm -rf claude-auto-clicker"
echo ""
echo "✅ 卸载完成！可以安全删除项目文件夹"
EOF

chmod +x uninstall.sh
echo "✅ 本地卸载脚本已创建"

echo ""
echo "🎉 本地安装完成！"
echo ""
echo "📁 所有文件都在当前目录中，无需担心污染系统"
echo ""
echo "📖 使用说明："
echo "1. 设置登录凭据: ./claude-auto-clicker login"
echo "2. 查看状态: ./claude-auto-clicker status"  
echo "3. 手动执行: ./claude-auto-clicker run"
echo "4. 启动 claude 命令时会自动触发后台点击"
echo ""
echo "📂 数据文件位置:"
echo "   - 配置文件: ./data/config.json"
echo "   - 日志文件: ./data/logs/"
echo "   - 虚拟环境: ./venv/ (如果创建了)"
echo ""
echo "🗑️  如需卸载:"
echo "   1. 运行卸载脚本: ./uninstall.sh"
echo "   2. 删除整个项目文件夹即可完全清理"
echo ""
echo "✨ 绿色软件模式：删除文件夹即可完全卸载！"