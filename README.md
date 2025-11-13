# 群组支付系统

## 项目介绍
这是一个群组支付管理系统，支持用户在群组中进行支付、查看交易记录和余额等功能。

## 运行步骤

### 1. 启动后端服务
```bash
uvicorn app.main:app --reload
```
后端服务将运行在 http://localhost:8000

### 2. 启动管理员端
在另一个终端窗口中运行：
```bash
streamlit run app_frontend.py
```
管理员端将可通过 http://localhost:8501 访问

### 3. 启动用户端
在第三个终端窗口中运行：
```bash
streamlit run user_frontend.py
```
用户端将可通过 http://localhost:8502 访问

## 注意事项
- 请确保后端服务已成功启动，然后再启动前端应用
- 每个命令需要在单独的终端窗口中运行，以确保服务持续运行
- 如需停止服务，可在对应的终端窗口中按 Ctrl+C 键