# AA 群组记账系统

## 项目介绍
AA群组记账系统是一个功能完整的群组财务管理平台，支持用户管理、群组管理、交易记录管理等核心功能。系统采用现代化的技术栈，提供了直观的用户界面和强大的管理员终端，方便用户进行群组财务的协作管理。

## 核心功能
- **用户管理**: 用户注册、登录、个人信息管理
- **群组管理**: 创建群组、管理群组成员、查看群组详情
- **交易管理**: 记录支出、AA制结算、自定义交易分配
- **余额追踪**: 实时查看群组成员的财务余额状态

## 系统架构
- **后端**: FastAPI (Python) - 提供高性能的RESTful API
- **数据库**: SQLite - 轻量级的文件数据库
- **前端**: Streamlit (Python) - 交互式Web界面
- **管理员终端**: 命令行界面 (Python) - 高级管理功能

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动后端服务器
系统提供了便捷的启动脚本：

```bash
# 使用脚本启动（推荐）
python start_server.py

# 或手动启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. 启动用户界面
```bash
streamlit run user_frontend.py
```

### 4. 启动管理员前端
```bash
streamlit run app_frontend.py
```

### 5. 启动管理员终端界面
```bash
python admin_terminal.py
```

## 系统配置

### 服务器配置
- **默认端口**: 8001
- **API基础URL**: http://localhost:8001
- **数据库文件**: group_payment.db

### 环境要求
- Python 3.8+
- pip 20.0+

## 用户认证系统

### 用户注册
新用户可以通过API或前端界面进行注册：
- **用户名**: 唯一标识符
- **密码**: 用于登录认证
- **公开信息**: 显示给其他用户的个人信息

### 用户登录
用户登录后可以访问系统功能：
- **登录接口**: POST /users/login
- **认证方式**: 用户名+密码验证

## 管理员终端使用说明

管理员终端提供了丰富的命令行操作，支持完整的用户管理、群组管理和交易管理功能。

### 基本命令
- `help`: 查看所有可用命令
- `exit`: 退出系统

### 用户管理命令
```
user create <用户名> <公开信息>      - 创建新用户
user list                           - 查看所有用户
user delete <用户ID>                - 删除用户
```

### 群组管理命令
```
group create <群组名> <用户ID1,用户ID2>  - 创建新群组
group list                          - 查看所有群组
group delete <群组ID>               - 删除群组
group detail <群组ID>               - 查看群组详情
group add_member <群组ID> <用户ID> <初始余额> - 添加成员到群组
group update_balance <群组ID> <用户ID> <余额变更> - 更新成员余额
```

### 交易管理命令
```
transaction create_custom <群组ID> <付款人ID> <总金额> <交易说明> <参与者列表> - 创建自定义交易
transaction create_aa <群组ID> <付款人ID> <总金额> <交易说明> <参与者ID列表> - 创建AA制交易
transaction list                    - 查看所有交易
transaction group <群组ID>          - 查看群组交易记录
```

## API接口文档

系统启动后，可以通过以下地址访问自动生成的API文档：
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 注意事项
1. 运行前端或管理员终端前，请确保后端服务器正在运行
2. 默认使用8001端口，避免与其他服务冲突
3. 首次启动时会自动创建数据库文件
4. 管理员终端提供了更强大的功能，适合系统管理员使用
5. 用户界面适合普通用户进行日常操作
6. 请妥善保管用户密码，系统暂不支持密码找回功能

## 故障排除

### 常见问题
- **服务器启动失败**: 检查端口是否被占用，尝试使用其他端口
- **数据库连接错误**: 确保有正确的文件权限，删除旧的数据库文件重新启动
- **API连接失败**: 检查服务器是否运行，URL配置是否正确

### 日志查看
服务器日志会显示在启动终端中，可以查看详细的错误信息和请求记录。

## 管理员终端使用说明

管理员终端提供了丰富的命令行操作，支持完整的用户管理、群组管理和交易管理功能。

### 基本命令
- `help`: 查看所有可用命令
- `exit`: 退出系统

### 用户管理命令
```
user create <用户名> <公开信息>      - 创建新用户
user list                           - 查看所有用户
user delete <用户ID>                - 删除用户
```

### 群组管理命令
```
group create <群组名> <用户ID1,用户ID2>  - 创建新群组
group list                          - 查看所有群组
group delete <群组ID>               - 删除群组
group detail <群组ID>               - 查看群组详情
group add_member <群组ID> <用户ID> <初始余额> - 添加成员到群组
group update_balance <群组ID> <用户ID> <余额变更> - 更新成员余额
```

### 交易管理命令
```
transaction create_custom <群组ID> <付款人ID> <总金额> <交易说明> <参与者列表> - 创建自定义交易
transaction create_aa <群组ID> <付款人ID> <总金额> <交易说明> <参与者ID列表> - 创建AA制交易
transaction list                    - 查看所有交易
transaction group <群组ID>          - 查看群组交易记录
```