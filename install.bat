@echo off
REM Claude Auto Clicker 安装脚本
echo Claude Auto Clicker 安装脚本
echo ================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 安装依赖
echo 正在安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 创建全局命令
echo 正在创建全局命令...
set "current_dir=%~dp0"
set "cmd_file=%current_dir%claude-auto-clicker.cmd"

REM 添加到 PATH（临时）
set "PATH=%PATH%;%current_dir%"

echo ✅ 安装完成！
echo.
echo 使用方法:
echo   claude-auto-clicker --help    查看帮助
echo   claude-auto-clicker login     设置登录凭据
echo   claude-auto-clicker status    查看状态
echo.
echo 注意: 当前会话中可以直接使用 claude-auto-clicker 命令
echo 要永久使用，请将以下路径添加到系统 PATH 环境变量:
echo %current_dir%
echo.
pause
