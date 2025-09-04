<<<<<<< HEAD
# Claude Auto Clicker

> 与 Claude Code 无缝集成的自动点击工具

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
- Chrome 浏览器

## 快速安装

### Linux/Mac

```bash
git clone https://github.com/your-username/claude-auto-clicker.git
cd claude-auto-clicker
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows

```cmd
git clone https://github.com/your-username/claude-auto-clicker.git
cd claude-auto-clicker
scripts\install.bat
```

## 使用方法

### 1. 配置登录凭据

首次使用需要设置登录账号密码：

```bash
claude-auto-clicker login
```

### 2. 查看配置状态

检查当前配置是否正确：

```bash
claude-auto-clicker status
```

### 3. 手动执行点击

测试点击功能是否正常：

```bash
claude-auto-clicker run
```

### 4. 启动 Claude Code

正常启动 claude 命令，自动点击功能会在后台运行：

```bash
claude
```

## 高级配置

### 自定义配置

设置自定义配置项：

```bash
# 设置点击间隔（秒）
claude-auto-clicker config click.click_interval 600

# 设置目标URL
claude-auto-clicker config target_url "https://your-target-site.com"

# 设置按钮XPath
claude-auto-clicker config click.button_xpath "//button[@id='your-button']"
```

### 配置文件位置

配置文件存储在用户主目录下：
- Linux/Mac: `~/.claude-auto-clicker/config.json`
- Windows: `%USERPROFILE%\.claude-auto-clicker\config.json`

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

## 日志文件

日志文件位置：
- Linux/Mac: `~/.claude-auto-clicker/logs/claude_auto_clicker.log`
- Windows: `%USERPROFILE%\.claude-auto-clicker\logs\claude_auto_clicker.log`

## 故障排除

### 1. 找不到按钮

如果点击失败，可能需要更新按钮的 XPath：

1. 打开目标网站
2. 右键点击目标按钮 → 检查
3. 在开发者工具中右键 HTML 元素 → Copy → Copy XPath
4. 使用命令更新配置：
   ```bash
   claude-auto-clicker config click.button_xpath "你的新XPath"
   ```

### 2. 登录失败

检查登录选择器是否正确：

```bash
# 查看当前配置
claude-auto-clicker status

# 更新选择器
claude-auto-clicker config login.username_selector "input[name='email']"
claude-auto-clicker config login.password_selector "input[name='pass']"
```

### 3. Claude 命令冲突

如果 claude 命令有问题，可以恢复原始命令：

```bash
# Linux/Mac
sudo mv $(which claude).original $(which claude)

# Windows
move "%CLAUDE_PATH%.original" "%CLAUDE_PATH%"
```

## 卸载

### Linux/Mac
```bash
~/.claude-auto-clicker/uninstall.sh
```

### Windows
```cmd
%USERPROFILE%\.claude-auto-clicker\uninstall.bat
```

## 安全说明

- 密码使用 Fernet 对称加密存储
- 加密密钥基于机器唯一标识生成
- 配置文件权限仅限当前用户访问
- 不会上传或发送任何用户数据

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题请提交 [Issue](https://github.com/your-username/claude-auto-clicker/issues)
=======
# claude-auto-clicker
自动点击恢复
>>>>>>> 98268f84af915ec97d19d17fd1b8435a6e6ccc68
