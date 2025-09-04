# Claude Auto Clicker

> 与 Claude Code 无缝集成的自动点击工具 - 绿色便携版

## ✨ 绿色软件特性

- 🗂️ **完全本地化** - 所有文件都在项目文件夹内
- 🔄 **便携安装** - 无需 pip install，不污染系统环境
- 🗑️ **一键卸载** - 删除文件夹即可完全清理
- 📁 **数据隔离** - 配置和日志都在项目内部

## 功能特性

- 🔐 **安全配置管理** - 加密存储登录凭据
- 🤖 **智能登录检测** - 自动检测并处理登录页面
- 🎯 **精准点击控制** - 支持自定义点击目标和时间间隔
- 🔧 **命令行界面** - 简单易用的命令行工具
- 🚀 **Claude Code 集成** - 启动 claude 命令时自动激活后台点击
- 📝 **详细日志记录** - 完整的操作日志和错误追踪
- 🌍 **跨平台支持** - 支持 Windows、Linux、macOS

## 安装要求

- Python 3.7 或更高版本
- Claude Code (必须先安装)
- 无需预装 Chromium/Chrome —— 安装脚本会自动下载便携版浏览器与匹配的 ChromeDriver 到项目目录

## 快速安装

### 方法1：使用安装脚本（推荐）

#### Linux/WSL/Mac（全自动）

```bash
# 下载项目
git clone https://github.com/your-username/claude-auto-clicker.git
cd claude-auto-clicker

# 一键安装（全自动）：
# - 自动创建并激活本地 venv
# - 安装依赖
# - 下载便携式 Chromium + ChromeDriver 到项目目录
# - 在无图形环境（WSL/服务器）自动启用无头模式
# - 安装完成后自动引导登录（输入账号与密码，覆盖保存）
chmod +x scripts/install.sh
./scripts/install.sh
```

#### Windows（全自动）

```cmd
# 下载项目
git clone https://github.com/your-username/claude-auto-clicker.git
cd claude-auto-clicker

:: 一键安装（全自动）：
:: - 安装依赖与包装器
:: - 下载便携式 Chromium + ChromeDriver 到项目目录
:: - 启用无头模式
:: - 安装完成后自动引导登录（输入账号与密码，覆盖保存）
scripts\install.bat
```

### 方法2：直接使用可执行文件（简单）

#### Windows

```cmd
# 1. 安装依赖
pip install -r requirements.txt

# 2. 直接使用
.\claude-auto-clicker.cmd --help
.\claude-auto-clicker.cmd login
```

#### Linux/Mac

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 直接使用
python claude-auto-clicker --help
python claude-auto-clicker login
```

## 📁 本地化文件结构

安装后，所有文件都在项目文件夹内：

```
claude-auto-clicker/
├── claude-auto-clicker          # 本地启动脚本（使用 python -m 运行 CLI）
├── browsers/                    # 便携式浏览器组件（安装时自动下载）
│   ├── chromium/               # Chromium 可执行文件（按平台）
│   ├── drivers/                # 匹配的 chromedriver 可执行文件
│   └── version.json            # 已下载版本信息
├── data/                        # 用户数据（自动创建）
│   ├── config.json             # 配置文件（加密存储密码）
│   └── logs/                   # 日志文件
├── venv/                        # 本地虚拟环境（安装时自动创建并激活）
├── uninstall.sh                 # 卸载脚本
└── [其他项目文件...]
```

## 使用方法

### 1. 配置登录凭据

安装脚本结束后会自动引导登录。如需手动执行或更新：

#### Windows
```cmd
.\claude-auto-clicker.cmd login           # 交互式输入（总是提示并覆盖保存）
# 或者自动化：
.\claude-auto-clicker.cmd login -u <用户名> -p <密码>
```

#### Linux/Mac
```bash
python claude-auto-clicker login           # 交互式输入（总是提示并覆盖保存）
# 或者自动化：
python claude-auto-clicker login -u <用户名> -p <密码>
```

### 2. 查看配置状态

#### Windows
```cmd
.\claude-auto-clicker.cmd status
```

#### Linux/Mac
```bash
python claude-auto-clicker status
```

### 3. 手动执行点击

#### Windows
```cmd
.\claude-auto-clicker.cmd run
```

#### Linux/Mac
```bash
python claude-auto-clicker run
```

### 4. 启动 Claude Code

正常启动 claude 命令，自动点击功能会在后台运行：

```bash
claude
```

## 高级配置

### 自定义配置

```bash
# 设置点击间隔（秒）
./claude-auto-clicker config click.click_interval 600

# 设置目标URL
./claude-auto-clicker config target_url "https://your-target-site.com"

# 设置按钮XPath
./claude-auto-clicker config click.button_xpath "//button[@id='your-button']"
```

### 配置文件位置

- 配置文件: `./data/config.json`
- 日志文件: `./data/logs/claude_auto_clicker.log`
- 便携式浏览器: `./browsers/`（Chromium 与 chromedriver 已固定匹配版本）

### 默认配置

```json
{
  "target_url": "https://www.aicodemirror.com/dashboard",
  "login": {
    "username": "",
    "password": "",
    "username_selector": "input[name='identifier']",
    "password_selector": "input[name='password']",
    "login_button_selector": "button[type='submit']"
  },
  "click": {
    "button_xpath": "/html/body/div[2]/div/div[4]/main/div/div/div/div[2]/div[2]/div[1]/div[2]/div/div[5]/button",
    "wait_timeout": 20,
    "click_interval": 300
  },
  "browser": {
    "headless": false,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
}
```

## 故障排除

### 1. 找不到按钮

如果点击失败，可能需要更新按钮的 XPath：

1. 打开目标网站
2. 右键点击目标按钮 → 检查
3. 在开发者工具中右键 HTML 元素 → Copy → Copy XPath
4. 使用命令更新配置：
   ```bash
   ./claude-auto-clicker config click.button_xpath "你的新XPath"
   ```

### 2. 登录失败

检查登录选择器是否正确：

```bash
# 查看当前配置
./claude-auto-clicker status

# 更新选择器
./claude-auto-clicker config login.username_selector "input[name='email']"
./claude-auto-clicker config login.password_selector "input[name='pass']"
```

### 3. Python 环境问题

如果出现 Python 相关错误：

```bash
# 检查虚拟环境是否激活
source ./venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### 4. 浏览器/驱动下载失败或网络受限

- 直接运行兜底脚本（与安装脚本使用相同逻辑）：
  ```bash
  python3 scripts/download_browsers.py
  ```
- Linux/WSL 必要运行库（如缺少）：
  ```bash
  sudo apt-get update && sudo apt-get install -y \
    fonts-liberation libasound2 libnss3 libx11-xcb1 libxi6 libxcomposite1 \
    libxcursor1 libxdamage1 libxfixes3 libxrandr2 libatk-bridge2.0-0 \
    libgtk-3-0 libxss1 libdrm2 libgbm1
  ```
- WSL/服务器默认已启用无头模式；如需关闭：
  ```bash
  ./claude-auto-clicker config browser.headless false
  ```

### 5. 团队共享与仓库体积

- 建议使用 Git LFS 跟踪 `browsers/**`，团队 clone 后即可使用，避免重复下载：
  ```bash
  git lfs install
  git lfs track "browsers/**"
  git add .gitattributes browsers
  git commit -m "vendor chromium + chromedriver via LFS"
  ```

## 🗑️ 卸载

### 方法1：使用卸载脚本（推荐）
```bash
./uninstall.sh
```

卸载脚本会：
- ✅ 恢复原始 claude 命令
- 🤔 询问是否删除 Chromium 浏览器
- 🧹 清理 webdriver-manager 缓存
- 📋 提示删除项目文件夹

### 方法2：手动完全清理
```bash
# 1. 恢复 claude 命令（如果需要）
sudo mv $(which claude).original $(which claude)

# 2. 删除 Chromium（可选）
sudo apt remove chromium-browser

# 3. 清理驱动缓存
rm -rf ~/.wdm

# 4. 删除项目文件夹
cd .. && rm -rf claude-auto-clicker
```

### 清理级别选择

| 清理级别 | 操作 | 结果 |
|---------|------|------|
| **基础** | 删除项目文件夹 | 保留浏览器和系统环境 |
| **标准** | `./uninstall.sh` + 保留浏览器 | 清理项目，保留浏览器供其他程序使用 |  
| **完全** | `./uninstall.sh` + 删除浏览器 | 完全清理，不留任何痕迹 |

## 🔒 安全说明

- 密码使用 Fernet 对称加密存储在本地
- 加密密钥基于机器唯一标识生成
- 所有配置文件都在本地项目目录中
- 不会上传或发送任何用户数据

## 🌟 优势对比

| 特性 | 传统安装方式 | 本项目（绿色版） |
|------|-------------|------------------|
| 安装位置 | 系统 Python 环境 | 项目文件夹内 |
| 配置文件 | 用户主目录 | 项目 data/ 目录 |
| 卸载方式 | pip uninstall + 手动清理 | 删除文件夹 |
| 环境污染 | 会影响系统环境 | 完全隔离 |
| 便携性 | 不便携 | 可整体移动 |

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题请提交 [Issue](https://github.com/your-username/claude-auto-clicker/issues)
