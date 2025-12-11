#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Group Payment System - 启动脚本
支持跨平台：Windows、macOS、Linux
"""

import os
import sys
import subprocess
import platform
import socket


def get_lan_ip():
    """
    获取局域网IP地址（跨平台）
    """
    try:
        # 创建一个临时的UDP连接来获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个公共DNS服务器（不需要实际通信）
            s.connect(('8.8.8.8', 80))
            lan_ip = s.getsockname()[0]
        return lan_ip
    except Exception:
        return "127.0.0.1"


def main():
    """
    主函数：启动FastAPI服务器
    """
    # 获取局域网IP
    lan_ip = get_lan_ip()
    
    # 显示启动信息
    print("🚀 正在启动 Group Payment System 服务器...")
    print(f"🌐 局域网访问地址: http://{lan_ip}:8001")
    print(f"🔧 API 文档地址: http://{lan_ip}:8001/docs")
    print("📋 按 Ctrl+C 停止服务器")
    print("-" * 40)
    
    # 构建启动命令
    command = [
        sys.executable,  # 使用当前Python解释器
        "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",  # 绑定到所有网络接口
        "--port", "8001",     # 使用8001端口（与实际运行的端口保持一致）
        "--reload"            # 启用热重载
    ]
    
    try:
        # 启动服务器
        print("启动命令:", " ".join(command))
        print("-" * 40)
        
        # 执行命令
        subprocess.run(command, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止（用户中断）")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 可能的解决方案：")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 检查端口8000是否被占用")
        print("3. 检查Python版本是否 >= 3.8")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()