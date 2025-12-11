#!/bin/bash

# 获取局域网IP地址（兼容macOS和Linux）
if command -v ipconfig &> /dev/null; then
    # macOS
    LAN_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "127.0.0.1")
elif command -v hostname &> /dev/null; then
    # Linux
    LAN_IP=$(hostname -I | awk '{print $1}')
else
    LAN_IP="127.0.0.1"
fi

# 启动 FastAPI 服务器，允许局域网访问
echo "🚀 正在启动 Group Payment System 服务器..."
echo "🌐 局域网访问地址: http://$LAN_IP:8000"
echo "🔧 API 文档地址: http://$LAN_IP:8000/docs"
echo "📋 按 Ctrl+C 停止服务器"
echo "----------------------------------------"

# 使用 uvicorn 启动服务器，绑定到 0.0.0.0 允许局域网访问
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload