#!/usr/bin/env python3
"""
Cherry Context Plugin 安装脚本
"""
import os
import sys
import subprocess

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ 是必需的")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def install_dependencies():
    """安装依赖"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_mcp.txt"])
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        sys.exit(1)

def initialize_plugin():
    """初始化插件"""
    try:
        from cherry_plugin.plugin import CherryContextPlugin
        plugin = CherryContextPlugin()
        print("✅ 插件初始化成功")
    except Exception as e:
        print(f"❌ 插件初始化失败: {e}")
        sys.exit(1)

def main():
    """主安装流程"""
    print("🍒 Cherry Context Plugin 安装程序")
    print("=" * 40)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    print("📦 安装依赖包...")
    install_dependencies()
    
    # 初始化插件
    print("🔧 初始化插件...")
    initialize_plugin()
    
    print("=" * 40)
    print("🎉 安装完成！")
    print("\n下一步:")
    print("1. 配置 Cherry Studio MCP 设置")
    print("2. 参考 README.md 开始使用")

if __name__ == "__main__":
    main()