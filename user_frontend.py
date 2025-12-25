import streamlit as st
import requests
import pandas as pd
import socket
import time

# 设置页面配置（必须是第一个Streamlit命令）
st.set_page_config(page_title="用户端 - AA 群组记账", page_icon="👤", layout="centered", initial_sidebar_state="expanded")

# 获取本地地址，确保与服务器保持一致
def get_local_ip():
    try:
        # 创建一个临时的UDP连接来获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个公共DNS服务器（不需要实际通信）
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "localhost"

# 使用本地地址，与服务器保持一致
API = f"http://{get_local_ip()}:8001"

# 添加自定义CSS样式
st.markdown("""
<style>
/* 覆盖Streamlit所有可能的选中单元格样式 - 最高优先级 */
.stDataFrame td,
.stDataFrame tr,
.stDataFrame table {
    --dataframe__cell--selected-background-color: rgba(0, 123, 255, 0.3) !important;
    --dataframe__cell--selected-border-color: rgba(0, 123, 255, 0.7) !important;
}

/* 直接覆盖单元格的所有选中、聚焦、激活状态 */
.stDataFrame td:focus,
.stDataFrame td:active,
.stDataFrame td[data-selected="true"],
.stDataFrame td:focus-within {
    background-color: rgba(0, 123, 255, 0.3) !important;
    border: 2px solid rgba(0, 123, 255, 0.7) !important;
    box-shadow: none !important;
    outline: none !important;
    -webkit-tap-highlight-color: transparent !important;
}

/* 处理悬停状态 */
.stDataFrame td:hover {
    background-color: rgba(0, 123, 255, 0.2) !important;
    border-color: rgba(0, 123, 255, 0.5) !important;
}

/* 确保表头样式不受影响 */
.stDataFrame th {
    background-color: #f0f2f6 !important;
}

/* 覆盖Streamlit内部样式 - 确保选中状态是蓝色 */
[data-testid="stDataFrame"] td:focus,
[data-testid="stDataFrame"] td:active,
[data-testid="stDataFrame"] td[data-selected="true"] {
    background-color: rgba(0, 123, 255, 0.3) !important;
    border: 2px solid rgba(0, 123, 255, 0.7) !important;
}

/* 增强悬停效果 */
[data-testid="stDataFrame"] td:hover {
    background-color: rgba(0, 123, 255, 0.2) !important;
    border-color: rgba(0, 123, 255, 0.5) !important;
}

/* 重置任何可能的默认选中样式 */
* {
    --primary-color: #007bff !important;
    --secondary-color: #007bff !important;
    --accent-color: #007bff !important;
}

/* 模态弹窗样式 - 使用更高优先级的选择器 */
div[data-modal="overlay"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    background-color: rgba(0, 0, 0, 0.5) !important;
    z-index: 9999 !important;
}

/* 模态框容器样式 - 使用更高优先级的选择器 */
div[data-modal="content"] {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    background-color: white !important;
    padding: 20px !important;
    border-radius: 8px !important;
    z-index: 10000 !important;
    width: 80% !important;
    max-width: 700px !important;
    max-height: 80vh !important;
    overflow-y: auto !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'user' not in st.session_state:
    st.session_state.user = None

# 主应用
if st.session_state.user is None:
    # 登录/注册页面切换
    tab1, tab2 = st.tabs(["登录", "注册"])
    
    with tab1:
        # 登录页面
        st.title("👤 用户登录")
        st.write("请输入您的用户名和密码进行登录")
        
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submit = st.form_submit_button("登录")
        
        if submit:
            if not username.strip():
                st.error("请输入用户名")
            elif not password:
                st.error("请输入密码")
            else:
                try:
                    # 调用登录API
                    response = requests.post(
                        f"{API}/users/login",
                        json={"name": username, "password": password}
                    )
                    if response.status_code == 200:
                        user_data = response.json()
                        st.session_state.user = user_data
                        st.success(f"登录成功！欢迎回来，{username}")
                        # 刷新页面显示登录后的内容
                        st.rerun()
                    else:
                        st.error(f"登录失败: {response.json().get('detail', '用户名或密码错误')}")
                except Exception as e:
                    st.error(f"登录出错: {str(e)}")
    
    with tab2:
        # 注册页面
        st.title("👤 用户注册")
        st.write("请输入您的用户名和密码进行注册")
        
        with st.form("register_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            public_info = st.text_area("公开信息（可选）")
            submit = st.form_submit_button("注册")
        
        if submit:
            if not username.strip():
                st.error("请输入用户名")
            elif not password:
                st.error("请输入密码")
            elif password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                try:
                    # 调用注册API
                    response = requests.post(
                        f"{API}/users/register",
                        json={
                            "name": username,
                            "password": password,
                            "public_info": public_info
                        }
                    )
                    if response.status_code == 200:
                        user_data = response.json()
                        st.session_state.user = user_data
                        st.success(f"注册成功！欢迎，{username}")
                        # 刷新页面显示登录后的内容
                        st.rerun()
                    else:
                        st.error(f"注册失败: {response.json().get('detail', '注册失败')}")
                except Exception as e:
                    st.error(f"注册出错: {str(e)}")
else:
    # 登录后的主页面
    user = st.session_state.user
    st.title(f"👤 欢迎回来，{user['name']}")
    
    # 登出按钮
    if st.button("退出登录"):
        st.session_state.user = None
        if 'user_groups' in st.session_state:
            del st.session_state.user_groups
        st.rerun()
    
    # 获取用户的群组信息并存储在会话状态中
    if 'user_groups' not in st.session_state:
        try:
            response = requests.get(f"{API}/users/{user['id']}/groups")
            if response.status_code == 200:
                data = response.json()
                st.session_state.user_groups = data['groups']
            else:
                st.session_state.user_groups = []
        except Exception as e:
            st.session_state.user_groups = []
            st.error(f"获取群组信息出错: {str(e)}")
    
    # ==================== 页面化设计开始 ====================
    # 使用标签页实现页面化导航
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 首页", "👥 群组详情", "🎫 使用兑换码", "📝 交易记录", "🎲 随机用户"])
    
    # ------------------------
    # 首页（第一个标签页）- 个人信息和群组余额
    # ------------------------
    with tab1:
        # 个人信息区块
        st.subheader("📋 个人信息")

        with st.container(border=True):  # 添加边框效果
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**用户名**: {user['name']}")
            with col2:
                st.info(f"**用户ID**: {user['id']}")
            if user.get('public_info'):
                st.success(f"**公开信息**: {user['public_info']}")
        
        st.divider()  # 添加水平分隔线
        
        st.subheader("📊 我的群组和余额")
        # 群组和余额区块
        with st.container(border=True):  # 添加边框效果
            # 首先显示群组信息（从会话状态或API获取）
            if st.session_state.user_groups:
                # 显示用户的群组列表和余额
                st.write(f"您好，{user['name']}，您加入了 {len(st.session_state.user_groups)} 个群组：")
                
                # 创建DataFrame展示群组信息
                group_data = []
                for g in st.session_state.user_groups:
                    # 获取群组详情以显示总成员数
                    try:
                        group_detail_response = requests.get(f"{API}/groups/{g['group_id']}")
                        total_members = 0
                        if group_detail_response.status_code == 200:
                            group_detail = group_detail_response.json()
                            # 优先使用members列表的长度，如果没有则使用total_members字段
                            total_members = len(group_detail.get('members', [])) if 'members' in group_detail else group_detail.get('total_members', 0)
                    except Exception as e:
                        st.error(f"获取群组 {g['group_name']} 详情出错: {str(e)}")
                        total_members = "获取失败"
                    
                    # 格式化余额显示
                    balance_str = f"{g['balance']:.2f}"
                    # 根据余额正负添加颜色
                    balance_color = "🟢" if g['balance'] >= 0 else "🔴"
                    
                    group_data.append([
                        g['group_id'],
                        g['group_name'],
                        f"{balance_color} {balance_str}",
                        total_members
                    ])
                
                df = pd.DataFrame(group_data, columns=["群组ID", "群组名称", "我的余额", "总成员数"], index=range(1, len(group_data)+1))
                st.dataframe(df, use_container_width=True)
                
                # 计算总余额
                total_balance = sum(g['balance'] for g in st.session_state.user_groups)
                st.metric("💰 所有群组总余额", f"{total_balance:.2f}")
            else:
                st.info("您还没有加入任何群组")
            
            # 添加刷新按钮到群组表单下方
            refresh_clicked = st.button("🔄 刷新")
            
            # 处理刷新逻辑
            if refresh_clicked:
                try:
                    response = requests.get(f"{API}/users/{user['id']}/groups")
                    if response.status_code == 200:
                        data = response.json()
                        # 更新会话中的群组信息
                        st.session_state.user_groups = data['groups']
                        st.rerun()  # 重新运行应用以更新显示
                    else:
                        st.error(f"获取群组信息失败: {response.text}")
                except Exception as e:
                    st.error(f"获取群组信息出错: {str(e)}")
    
    # ==================== 关键修复：确保 tab2 区块正确闭合 ====================
    # ------------------------
    # 群组详情（第二个标签页）
    # ------------------------
    # 在登录后的主页面部分，修改群组详情标签页中的侧边栏代码：
    with tab2:
        # 添加创建群组按钮
        col1, col2 = st.columns([1, 0.1])
        with col1:
            st.subheader("👥 群组详情")
        with col2:
            # 显示创建群组按钮
            if st.button("➕", key="create_group_button", help="创建新群组"):
                st.session_state.show_create_group = True
        
        # 初始化用户ID列表的状态
        if 'user_id_input' not in st.session_state:
            st.session_state.user_id_input = ""
        
        # 在侧边栏显示创建群组表单
        if st.session_state.get('show_create_group', False):
            with st.sidebar:
                st.header("➕ 创建新群组")
                
                # 关闭按钮
                if st.button("❌ 关闭", key="close_create_group"):
                    st.session_state.show_create_group = False
                    st.rerun()
                
                # 创建群组表单
                st.write("---")
                st.subheader("📝 创建群组")

                # 使用表单包装创建群组功能
                with st.form(key="create_group_final_form"):
                    group_name = st.text_input("群组名称", placeholder="输入新群组的名称")
                    
                    # 简化的提示信息
                    st.info("创建后，您可以在群组详情中添加其他成员")
                    
                    # 提交按钮
                    create_clicked = st.form_submit_button("✅ 创建群组", use_container_width=True)
                    
                    if create_clicked:
                        if not group_name.strip():
                            st.error("请输入群组名称")
                        else:
                            # 只包含当前用户自己的群组
                            user_ids = {user['id']}
                            
                            with st.spinner("正在创建群组..."):
                                try:
                                    # 创建群组
                                    response = requests.post(
                                        f"{API}/groups",
                                        json={
                                            "name": group_name,
                                            "member_ids": list(user_ids)
                                        }
                                    )
                                    
                                    if response.status_code == 200:
                                        group_data = response.json()
                                        st.success(f"✅ 群组创建成功！")
                                        st.write(f"**群组名称:** {group_data['name']}")
                                        st.write(f"**群组ID:** {group_data['id']}")
                                        
                                        # 清理状态
                                        if 'user_id_input' in st.session_state:
                                            del st.session_state.user_id_input
                                        if 'search_triggered' in st.session_state:
                                            del st.session_state.search_triggered
                                        
                                        # 刷新群组信息
                                        if 'user_groups' in st.session_state:
                                            del st.session_state.user_groups
                                        
                                        # 关闭侧边栏
                                        st.session_state.show_create_group = False
                                        st.rerun()
                                    else:
                                        error_detail = response.json().get('detail', '创建失败')
                                        st.error(f"❌ 创建群组失败: {error_detail}")
                                except Exception as e:
                                    st.error(f"创建群组出错: {str(e)}")
        
        # 群组详情显示（原功能）
        with st.container(border=True):
            # 从用户所在的群组中选择
            if st.session_state.user_groups:
                group_options = [(g['group_name'], g['group_id']) for g in st.session_state.user_groups]
                selected_group = st.selectbox(
                    "选择群组查看详情",
                    options=group_options,
                    format_func=lambda x: x[0],
                    index=None,
                    placeholder="选择要查看的群组..."
                )
                
                if selected_group:
                    try:
                        response = requests.get(f"{API}/groups/{selected_group[1]}")
                        if response.status_code == 200:
                            group_detail = response.json()
                            st.subheader(f"📊 {group_detail['name']} - 群组详情")
                            
                            # 显示群组信息
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"**群组ID:** {group_detail['id']}")
                            with col2:
                                st.info(f"**创建时间:** {group_detail.get('created_at', '未知')}")
                            
                            # 显示成员列表
                            st.subheader("👥 成员列表")
                            members = group_detail.get('members', [])
                            
                            if members:
                                # 检查当前用户是否是领导者（简化版本）
                                current_user_is_leader = False
                                current_user_id = user['id']
                                
                                # 遍历成员列表，检查当前用户是否是领导者
                                for member in members:
                                    # 获取用户信息（兼容不同的响应结构）
                                    member_user_id = member.get('user_id') or member.get('user', {}).get('id')
                                    is_leader = member.get('is_leader', False)
                                    
                                    if member_user_id == current_user_id and is_leader:
                                        current_user_is_leader = True
                                        break
                                
                                # 直接显示添加成员功能（临时测试版本）
                                st.subheader("➕ 添加成员")
                                with st.form(key="add_member_form"):
                                    new_member_id = st.text_input("新成员ID", placeholder="输入要添加的用户ID")
                                    add_member_clicked = st.form_submit_button("添加成员")
                                    
                                    if add_member_clicked:
                                        if not new_member_id.strip():
                                            st.error("请输入成员ID")
                                        else:
                                            try:
                                                new_member_id_int = int(new_member_id.strip())
                                                # 调用添加成员API
                                                response = requests.post(
                                                    f"{API}/groups/{selected_group[1]}/add_member",
                                                    json={
                                                        "current_user_id": user['id'],
                                                        "user_id": new_member_id_int
                                                    }
                                                )
                                                if response.status_code == 200:
                                                    st.success("✅ 成员添加成功")
                                                    st.rerun()
                                                else:
                                                    error_detail = response.json().get('detail', '添加失败')
                                                    st.error(f"❌ 添加成员失败: {error_detail}")
                                            except ValueError:
                                                st.error("请输入有效的用户ID")
                                            except Exception as e:
                                                st.error(f"添加成员出错: {str(e)}")
                                                st.error(f"API调用详情: {e.response.text if hasattr(e, 'response') else '无详细信息'}")
                                member_data = []
                                for member in members:
                                    # 获取成员的用户信息和余额
                                    member_user = member.get('user', {})
                                    member_name = member_user.get('name', '未知用户')
                                    member_balance = member.get('balance', 0)
                                    member_role = "👑 领导者" if member.get('is_leader') else "成员"
                                    
                                    # 格式化余额显示
                                    balance_str = f"{member_balance:.2f}"
                                    balance_color = "🟢" if member_balance >= 0 else "🔴"
                                    
                                    member_data.append([
                                        member.get('user_id'),
                                        member_name,
                                        member_role,
                                        f"{balance_color} {balance_str}"
                                    ])
                                
                                member_df = pd.DataFrame(member_data, columns=["成员ID", "成员名称", "角色", "余额"], index=range(1, len(member_data)+1))
                                st.dataframe(member_df, use_container_width=True)
                            else:
                                st.info("该群组暂无成员")
                            
                            # 发起AA交易功能
                            st.subheader("💰 发起AA交易")
                            with st.form(key="create_aa_transaction"):
                                # 输入交易信息
                                description = st.text_input("交易描述", placeholder="例如：聚餐、购物等")
                                total_amount = st.number_input("总金额", min_value=0.01, step=0.01, format="%.2f")
                                
                                # 选择参与者
                                st.write("选择参与者（可以多选）")
                                
                                # 创建参与者选择字典
                                participant_options = {}
                                for member in members:
                                    member_user = member.get('user', {})
                                    member_name = member_user.get('name', '未知用户')
                                    participant_options[f"{member_name} (ID: {member.get('user_id')})"] = member.get('user_id')
                                
                                # 多选参与者
                                selected_participants = st.multiselect(
                                    "选择参与者",
                                    options=list(participant_options.keys())
                                )
                                
                                # 提交按钮
                                create_aa_clicked = st.form_submit_button("✅ 发起AA交易")
                                
                                if create_aa_clicked:
                                    if not description.strip():
                                        st.error("请输入交易描述")
                                    elif total_amount <= 0:
                                        st.error("请输入有效的总金额")
                                    elif not selected_participants:
                                        st.error("请至少选择一个参与者")
                                    else:
                                        # 提取参与者ID
                                        participant_ids = [participant_options[name] for name in selected_participants]
                                        
                                        # 确保发起者自己在参与者列表中
                                        if user['id'] not in participant_ids:
                                            participant_ids.append(user['id'])
                                            
                                        # 计算每人分摊金额
                                        per_person_amount = total_amount / len(participant_ids)
                                        
                                        with st.spinner("正在发起AA交易..."):
                                            try:
                                                # 调用API创建交易
                                                response = requests.post(
                                                    f"{API}/transactions",
                                                    json={
                                                        "group_id": selected_group[1],
                                                        "payer_id": user['id'],
                                                        "total_amount": total_amount,
                                                        "description": description,
                                                        "participants": participant_ids
                                                    }
                                                )
                                                
                                                if response.status_code == 200:
                                                    transaction_data = response.json()
                                                    st.success(f"✅ AA交易发起成功！")
                                                    st.write(f"**交易ID:** {transaction_data['transaction_id']}")
                                                    st.write(f"**总金额:** {transaction_data['total']} 元")
                                                    st.write(f"**参与人数:** {len(participant_ids)} 人")
                                                    st.write(f"**每人分摊:** {per_person_amount:.2f} 元")
                                                    # 刷新页面
                                                    st.rerun()
                                                else:
                                                    error_detail = response.json().get('detail', '创建交易失败')
                                                    st.error(f"❌ 发起AA交易失败: {error_detail}")
                                            except Exception as e:
                                                st.error(f"发起AA交易出错: {str(e)}")
                            
                            # 显示交易记录
                            st.subheader("📝 交易记录")
                            try:
                                # 获取交易记录
                                response = requests.get(f"{API}/transactions")
                                if response.status_code == 200:
                                    all_transactions = response.json()
                                    # 过滤当前群组的交易
                                    group_transactions = [t for t in all_transactions if t['group_id'] == selected_group[1]]
                                    
                                    if group_transactions:
                                        transaction_data = []
                                        for t in group_transactions:
                                            # 获取参与者信息
                                            participants = t.get('participants', [])
                                            participant_names = [p['user']['name'] for p in participants]
                                            
                                            transaction_data.append([
                                                t['id'],
                                                t['description'],
                                                f"{t['total_amount']:.2f}",
                                                ', '.join(participant_names[:3]) + (f" 等{len(participants)}人" if len(participants) > 3 else ""),
                                                t['created_at']
                                            ])
                                    else:
                                        transaction_data = []
                                else:
                                    transaction_data = []
                            except Exception as e:
                                st.error(f"获取交易记录出错: {str(e)}")
                                transaction_data = []
                                
                            # 显示交易记录表格
                            if transaction_data:
                                transaction_df = pd.DataFrame(transaction_data, columns=["交易ID", "描述", "总金额", "参与者", "创建时间"], index=range(1, len(transaction_data)+1))
                                st.dataframe(transaction_df, use_container_width=True)
                            else:
                                st.info("该群组暂无交易记录")
                        else:
                            st.error(f"获取群组详情失败: {response.text}")
                    except Exception as e:
                        st.error(f"获取群组详情出错: {str(e)}")
            else:
                st.info("您还没有加入任何群组")
    
    # ==================== 确保下面的标签页在正确的位置 ====================
    # ------------------------
    # 使用兑换码（第三个标签页）
    # ------------------------
    with tab3:
        st.subheader("🎫 使用兑换码")
        with st.container(border=True):  # 添加边框效果
            # 兑换码输入框
            code = st.text_input("请输入兑换码", max_chars=10, placeholder="例如: ABC1234567")
            
            # 兑换按钮
            if st.button("💡 兑换"):
                if not code.strip():
                    st.error("请输入兑换码")
                else:
                    try:
                        # 调用兑换码API
                        response = requests.post(
                            f"{API}/redeem_code",
                            json={
                                "code": code,
                                "user_id": user['id']
                            }
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"兑换成功！获得: {data['amount']} 元")
                            # 刷新用户信息
                            response = requests.get(f"{API}/users/{user['id']}")
                            if response.status_code == 200:
                                st.session_state.user = response.json()
                                st.rerun()
                        else:
                            st.error(f"兑换失败: {response.json().get('detail', '兑换码无效')}")
                    except Exception as e:
                        st.error(f"兑换出错: {str(e)}")
    
    # ------------------------
    # 交易记录（第四个标签页）
    # ------------------------
    with tab4:
        st.subheader("📝 交易记录")
        with st.container(border=True):  # 添加边框效果
            try:
                # 获取交易记录
                response = requests.get(f"{API}/transactions")
                if response.status_code == 200:
                    all_transactions = response.json()
                    
                    # 过滤当前用户参与的交易
                    user_transactions = []
                    current_user_id = user['id']
                    
                    for tx in all_transactions:
                        # 检查当前用户是否是参与者
                        for participant in tx.get('participants', []):
                            if participant['user_id'] == current_user_id:
                                # 提取有用信息
                                tx_info = {
                                    'transaction_id': tx['id'],
                                    'group_id': tx['group_id'],
                                    'total_amount': tx['total_amount'],
                                    'description': tx['description'],
                                    'created_at': tx['created_at'],
                                    'is_payer': tx['payer_id'] == current_user_id,
                                    'my_share': participant['share_amount']
                                }
                                user_transactions.append(tx_info)
                                break
                    
                    if user_transactions:
                        # 转换为DataFrame
                        df = pd.DataFrame(user_transactions)
                        
                        # 确保时间列存在并转换为datetime类型
                        if 'created_at' in df.columns:
                            df['created_at'] = pd.to_datetime(df['created_at'])
                            # 按时间倒序排列
                            df = df.sort_values(by='created_at', ascending=False)
                        
                        # 选择要显示的列
                        display_columns = ['transaction_id', 'description', 'total_amount', 'my_share', 'is_payer', 'created_at']
                        
                        # 重命名列
                        df = df.rename(columns={
                            'transaction_id': '交易ID',
                            'description': '描述',
                            'total_amount': '总金额',
                            'my_share': '我的分摊',
                            'is_payer': '我是付款人',
                            'created_at': '创建时间',
                            'group_id': '群组ID'
                        })
                        
                        # 格式化金额显示
                        for col in ['总金额', '我的分摊']:
                            if col in df.columns:
                                df[col] = df[col].apply(lambda x: f"¥{x:.2f}")
                        
                        # 格式化布尔值显示
                        if '我是付款人' in df.columns:
                            df['我是付款人'] = df['我是付款人'].map({True: '是', False: '否'})
                        
                        # 显示交易记录
                        st.dataframe(df[['交易ID', '描述', '总金额', '我的分摊', '我是付款人', '创建时间']], use_container_width=True)
                    else:
                        st.info("暂无交易记录")
                else:
                    st.error(f"获取交易记录失败: {response.text}")
            except Exception as e:
                st.error(f"获取交易记录出错: {str(e)}")
    
    # ------------------------
    # 随机用户（第五个标签页）
    # ------------------------
    with tab5:
        st.subheader("🎲 随机用户")
        with st.container(border=True):  # 添加边框效果
            # 获取随机用户信息
            if st.button("🎲 获取随机用户"):
                try:
                    response = requests.get(f"{API}/users/random")
                    if response.status_code == 200:
                        random_user = response.json()
                        st.success("✅ 获取随机用户成功")
                        
                        # 显示随机用户信息
                        with st.container(border=True):
                            st.subheader("👤 随机用户信息")
                            st.markdown(f"**用户名:** {random_user['name']}")
                            st.markdown(f"**用户ID:** {random_user['id']}")
                            if random_user.get('public_info'):
                                st.markdown(f"**公开信息:** {random_user['public_info']}")
                    else:
                        st.error(f"获取随机用户失败: {response.text}")
                except Exception as e:
                    st.error(f"获取随机用户出错: {str(e)}")