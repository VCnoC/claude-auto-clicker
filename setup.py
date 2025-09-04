"""
Claude Auto Clicker 安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
this_directory = Path(__file__).parent
long_description = ""
if (this_directory / "README.md").exists():
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取依赖
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt", 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="claude-auto-clicker",
    version="1.0.0",
    author="Claude Auto Clicker Team",
    author_email="",
    description="与 Claude Code 无缝集成的自动点击工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/claude-auto-clicker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-auto-clicker=claude_auto_clicker.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "claude_auto_clicker": ["templates/*.json"],
    },
    keywords="automation selenium claude-code web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/your-username/claude-auto-clicker/issues",
        "Source": "https://github.com/your-username/claude-auto-clicker",
    },
)