"""
命令行接口模块
"""
import click
import getpass
from pathlib import Path
from .config import config_manager
from .core.auto_clicker import auto_clicker
from .utils.logger import logger
from .utils.browser_downloader import ChromiumDownloader


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Claude Auto Clicker - 与 Claude Code 集成的自动点击工具"""
    pass


@cli.command()
def login():
    """设置登录凭据"""
    click.echo("设置登录凭据")
    click.echo("=" * 30)
    
    username = click.prompt("请输入用户名")
    password = getpass.getpass("请输入密码: ")
    
    if not username or not password:
        click.echo("❌ 用户名和密码不能为空")
        return
    
    try:
        config_manager.set_login_credentials(username, password)
        click.echo("✅ 登录凭据设置成功")
    except Exception as e:
        click.echo(f"❌ 设置失败: {e}")


@cli.command()
def status():
    """查看当前配置状态"""
    click.echo("当前配置状态")
    click.echo("=" * 30)
    
    # 检查登录配置
    if config_manager.is_configured():
        username, _ = config_manager.get_login_credentials()
        click.echo(f"✅ 登录已配置 (用户名: {username})")
    else:
        click.echo("❌ 未配置登录凭据，请运行 'claude-auto-clicker login'")
    
    # 检查浏览器状态
    project_root = Path(__file__).parent.parent
    downloader = ChromiumDownloader(project_root)
    
    if downloader.is_installed():
        chromium_path = downloader.get_chromium_path()
        click.echo(f"✅ 便携式 Chromium: {chromium_path}")
    else:
        click.echo("❌ 便携式 Chromium 未安装，请运行 'claude-auto-clicker install-chromium'")
        # 检查系统浏览器
        clicker_instance = auto_clicker.__class__()
        system_chromium = clicker_instance._get_chromium_path()
        if system_chromium:
            click.echo(f"⚠️  系统 Chromium: {system_chromium}")
        else:
            click.echo("❌ 未找到任何可用的浏览器")
    
    # 显示其他配置信息
    config = config_manager.load_config()
    click.echo(f"🌐 目标URL: {config.get('target_url', '未配置')}")
    click.echo(f"🔘 点击间隔: {config.get('click', {}).get('click_interval', 300)} 秒")
    click.echo(f"⏱️  等待超时: {config.get('click', {}).get('wait_timeout', 20)} 秒")
    
    # 显示配置文件位置
    click.echo(f"📁 配置文件: {config_manager.config_file}")
    click.echo(f"📁 项目目录: {project_root}")


@cli.command()
def run():
    """手动执行一次点击任务"""
    if not config_manager.is_configured():
        click.echo("❌ 未配置登录凭据，请先运行 'claude-auto-clicker login'")
        return
    
    click.echo("开始执行点击任务...")
    
    try:
        success = auto_clicker.perform_single_click()
        if success:
            click.echo("✅ 点击任务执行成功")
        else:
            click.echo("❌ 点击任务执行失败，请检查日志")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}")


@cli.command()
@click.option('--interval', '-i', default=None, type=int, help='点击间隔（秒）')
def start(interval):
    """开始连续点击模式"""
    if not config_manager.is_configured():
        click.echo("❌ 未配置登录凭据，请先运行 'claude-auto-clicker login'")
        return
    
    if interval is None:
        interval = config_manager.get_config_value('click.click_interval', 300)
    
    click.echo(f"开始连续点击模式，间隔 {interval} 秒")
    click.echo("按 Ctrl+C 停止")
    
    try:
        auto_clicker.start_continuous_clicking(interval)
    except KeyboardInterrupt:
        click.echo("\n✅ 已停止连续点击")
    except Exception as e:
        click.echo(f"❌ 执行失败: {e}")


@cli.command()
@click.argument('key')
@click.argument('value')
def config(key, value):
    """设置配置项"""
    try:
        # 尝试转换数值类型
        if value.isdigit():
            value = int(value)
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        
        config_manager.set_config_value(key, value)
        click.echo(f"✅ 配置项 {key} 已设置为: {value}")
    except Exception as e:
        click.echo(f"❌ 设置失败: {e}")


@cli.command(name='install-chromium')
@click.option('--force', is_flag=True, help='强制重新下载，即使已安装')
def install_chromium(force):
    """下载并安装便携式 Chromium 浏览器"""
    project_root = Path(__file__).parent.parent
    downloader = ChromiumDownloader(project_root)
    
    click.echo("便携式 Chromium 安装器")
    click.echo("=" * 30)
    
    # 检查是否已安装
    if downloader.is_installed() and not force:
        chromium_path = downloader.get_chromium_path()
        click.echo(f"✅ 便携式 Chromium 已安装: {chromium_path}")
        
        if not click.confirm("是否重新下载安装？"):
            return
    
    click.echo("正在下载 Chromium，这可能需要几分钟...")
    
    try:
        if downloader.download_and_install():
            chromium_path = downloader.get_chromium_path()
            click.echo(f"✅ Chromium 安装成功: {chromium_path}")
            click.echo("现在可以使用 'claude-auto-clicker run' 测试自动点击功能")
        else:
            click.echo("❌ Chromium 安装失败，请检查网络连接和日志")
    except Exception as e:
        click.echo(f"❌ 安装过程中发生错误: {e}")


@cli.command(name='uninstall-chromium')
def uninstall_chromium():
    """卸载便携式 Chromium 浏览器"""
    project_root = Path(__file__).parent.parent
    downloader = ChromiumDownloader(project_root)
    
    if not downloader.is_installed():
        click.echo("便携式 Chromium 未安装")
        return
    
    if click.confirm("确认卸载便携式 Chromium？"):
        if downloader.uninstall():
            click.echo("✅ 便携式 Chromium 已卸载")
        else:
            click.echo("❌ 卸载失败")


def main():
    """主入口函数"""
    cli()