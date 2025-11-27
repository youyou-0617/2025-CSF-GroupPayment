# Group Payment System - 局域网部署指南

## 🚀 部署状态
✅ 服务已成功部署到局域网！

**局域网访问地址:** http://172.16.9.232:8000
**API 文档地址:** http://172.16.9.232:8000/docs

## 📋 功能说明

### 主要特性
- ✅ FastAPI 框架构建的高性能 API 服务
- ✅ 局域网内多设备访问支持
- ✅ 实时热重载（代码修改后自动重启）
- ✅ 完整的 API 文档（Swagger UI）

### 可用的 API 端点
- **用户管理**: `/users`
- **群组管理**: `/groups`
- **交易管理**: `/transactions`
- **完整文档**: `/docs`

## 🖥️ 从其他电脑访问

### Windows 电脑
1. 打开浏览器（Chrome、Edge 等）
2. 在地址栏输入：`http://172.16.9.232:8000`
3. 访问 API 文档：`http://172.16.9.232:8000/docs`

### Mac 电脑
1. 打开 Safari 或 Chrome 浏览器
2. 在地址栏输入：`http://172.16.9.232:8000`
3. 访问 API 文档：`http://172.16.9.232:8000/docs`

### 移动设备
1. 确保手机连接到同一 WiFi 网络
2. 打开浏览器
3. 在地址栏输入：`http://172.16.9.232:8000`

## 🛠️ 如何启动服务

### 方法 1：使用启动脚本（推荐）
```bash
# 给脚本添加执行权限（仅需一次）
chmod +x start_server.sh

# 启动服务器
./start_server.sh
```

### 方法 2：手动启动
```bash
# 使用 uvicorn 直接启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法 3：使用 Python 脚本（跨平台）
```bash
# 启动服务器
python start_server.py
```

## 📊 启动输出说明

当你启动服务器时，会看到类似以下输出：
```
🚀 正在启动 Group Payment System 服务器...
🌐 局域网访问地址: http://172.16.9.232:8000
🔧 API 文档地址: http://172.16.9.232:8000/docs
📋 按 Ctrl+C 停止服务器
----------------------------------------
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

## 🧪 测试连接

### 从本机测试
```bash
# 使用 curl 测试
curl http://localhost:8000/groups

# 或使用浏览器访问
http://localhost:8000
```

### 从其他设备测试
```bash
# 在其他电脑上使用 curl 测试
curl http://172.16.9.232:8000/groups
```

## 🔧 常见问题解决

### 问题：其他设备无法访问服务
**解决方案：**
1. 检查所有设备是否在同一 WiFi/局域网下
2. 确认防火墙没有阻止 8000 端口
3. 检查 IP 地址是否正确（使用 `ifconfig` 或 `ipconfig` 查看）

### 问题：端口被占用
**解决方案：**
```bash
# 修改端口号（例如使用 8080 端口）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 问题：启动失败
**解决方案：**
1. 检查依赖是否安装：`pip install -r requirements.txt`
2. 确保 Python 版本 >= 3.8
3. 查看错误信息并解决相应问题

## 📱 客户端应用

### 管理员终端
```bash
# 运行管理员终端
python admin_terminal.py
```

### 用户前端
```bash
# 运行用户前端
python user_frontend.py
```

### 应用前端
```bash
# 运行应用前端
python app_frontend.py
```

## 📋 停止服务
- 在启动服务的终端窗口中，按 `Ctrl+C` 停止服务
- 或关闭终端窗口

## 🔒 安全说明

- 此部署仅适用于内部局域网使用
- 不建议在公共网络上部署此服务
- 服务默认不设置认证，请注意数据安全
- 不要在生产环境中使用此配置

## 🆕 更新服务

1. 修改代码文件（会自动热重载）
2. 如果修改了依赖，需要重新安装：`pip install -r requirements.txt`
3. 如果遇到问题，重启服务即可

---

**🎉 恭喜！你的 Group Payment System 现在可以在局域网内的所有设备上使用了！**