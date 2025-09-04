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

# 创建虚拟环境（可选）
read -p "是否要创建虚拟环境？(y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv ~/.claude-auto-clicker-env
    source ~/.claude-auto-clicker-env/bin/activate
    echo "✅ 虚拟环境已创建并激活"
fi

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 安装本地包
echo "📦 安装 Claude Auto Clicker..."
pip install -e .

# 备份原始 claude 命令
claude_path=$(which claude)
if [ -f "$claude_path" ] && [ ! -f "${claude_path}.original" ]; then
    echo "💾 备份原始 claude 命令..."
    sudo cp "$claude_path" "${claude_path}.original"
fi

# 安装包装器
wrapper_script="$PWD/scripts/claude_wrapper.py"
if [ -f "$wrapper_script" ]; then
    echo "🔧 安装 claude 命令包装器..."
    sudo cp "$wrapper_script" "$claude_path"
    sudo chmod +x "$claude_path"
    echo "✅ 包装器安装完成"
fi

# 创建卸载脚本
cat > ~/.claude-auto-clicker/uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️  卸载 Claude Auto Clicker..."

# 恢复原始 claude 命令
claude_path=$(which claude)
if [ -f "${claude_path}.original" ]; then
    sudo mv "${claude_path}.original" "$claude_path"
    echo "✅ 已恢复原始 claude 命令"
fi

# 卸载 pip 包
pip uninstall claude-auto-clicker -y 2>/dev/null || true

# 删除配置目录
read -p "是否删除配置文件和日志？(y/n): " delete_config
if [[ $delete_config =~ ^[Yy]$ ]]; then
    rm -rf ~/.claude-auto-clicker
    echo "✅ 配置文件已删除"
fi

echo "✅ 卸载完成"
EOF

chmod +x ~/.claude-auto-clicker/uninstall.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "📖 使用说明："
echo "1. 设置登录凭据: claude-auto-clicker login"
echo "2. 查看状态: claude-auto-clicker status"  
echo "3. 手动执行: claude-auto-clicker run"
echo "4. 启动 claude 命令时会自动触发后台点击"
echo ""
echo "🗑️  如需卸载，请运行: ~/.claude-auto-clicker/uninstall.sh"