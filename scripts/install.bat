@echo off
REM Claude Auto Clicker 安装脚本 (Windows)

echo 🚀 开始安装 Claude Auto Clicker...

REM 检查 Python 版本
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo ✅ Python 检查通过

REM 检查是否已安装 Claude Code
claude --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未找到 claude 命令
    echo 请先安装 Claude Code: https://claude.ai/code
    pause
    exit /b 1
)

echo ✅ 检测到 Claude Code

REM 创建配置目录
if not exist "%USERPROFILE%\.claude-auto-clicker" (
    mkdir "%USERPROFILE%\.claude-auto-clicker"
)

REM 安装依赖
echo 📦 安装依赖包...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 安装本地包
echo 📦 安装 Claude Auto Clicker...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 安装失败
    pause
    exit /b 1
)

REM 获取 claude 命令路径
for /f "tokens=*" %%i in ('where claude') do set CLAUDE_PATH=%%i

REM 备份原始 claude 命令
if exist "%CLAUDE_PATH%" (
    if not exist "%CLAUDE_PATH%.original" (
        echo 💾 备份原始 claude 命令...
        copy "%CLAUDE_PATH%" "%CLAUDE_PATH%.original"
    )
)

REM 安装包装器
echo 🔧 安装 claude 命令包装器...
copy /y "scripts\claude_wrapper.py" "%CLAUDE_PATH%"

REM 创建卸载脚本
echo @echo off > "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo echo 🗑️  卸载 Claude Auto Clicker... >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo. >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo REM 恢复原始 claude 命令 >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo if exist "%CLAUDE_PATH%.original" ( >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo     move "%CLAUDE_PATH%.original" "%CLAUDE_PATH%" >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo     echo ✅ 已恢复原始 claude 命令 >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo ) >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo. >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo REM 卸载 pip 包 >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo pip uninstall claude-auto-clicker -y >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo. >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo set /p delete_config="是否删除配置文件和日志？(y/n): " >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo if /i "%%delete_config%%"=="y" ( >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo     rmdir /s /q "%USERPROFILE%\.claude-auto-clicker" >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo     echo ✅ 配置文件已删除 >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo ) >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo. >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo echo ✅ 卸载完成 >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"
echo pause >> "%USERPROFILE%\.claude-auto-clicker\uninstall.bat"

echo.
echo 🎉 安装完成！
echo.
echo 📖 使用说明：
echo 1. 设置登录凭据: claude-auto-clicker login
echo 2. 查看状态: claude-auto-clicker status
echo 3. 手动执行: claude-auto-clicker run
echo 4. 启动 claude 命令时会自动触发后台点击
echo.
echo 🗑️  如需卸载，请运行: %USERPROFILE%\.claude-auto-clicker\uninstall.bat

REM 自动下载便携式浏览器组件并启用无头模式（含兜底）
echo 📦 正在下载浏览器组件 (Chromium + ChromeDriver)...
claude-auto-clicker download-browsers --force
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  CLI 子命令不可用，尝试 python 模块方式...
    py -3 -m claude_auto_clicker.cli download-browsers --force
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️  模块方式失败，尝试直接脚本...
        py -3 scripts\download_browsers.py
        if %ERRORLEVEL% NEQ 0 (
            echo ❌ 浏览器组件下载失败，可稍后手动运行其中任一命令：
            echo    claude-auto-clicker download-browsers --force
            echo    或 py -3 -m claude_auto_clicker.cli download-browsers --force
            echo    或 py -3 scripts\download_browsers.py
        ) else (
            echo ✅ 浏览器组件安装完成（通过脚本）
        )
    ) else (
        echo ✅ 浏览器组件安装完成（通过 python 模块）
    )
) else (
    echo ✅ 浏览器组件安装完成（通过 CLI）
)

echo 🖥️  启用无头模式
claude-auto-clicker config browser.headless true

pause
