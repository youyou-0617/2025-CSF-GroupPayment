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
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap");

:root {
    --brand: #0f766e;
    --brand-strong: rgba(15, 118, 110, 0.7);
    --brand-soft: rgba(15, 118, 110, 0.3);
    --brand-hover: rgba(15, 118, 110, 0.18);
    --accent: #f97316;
    --ink: #0b1220;
    --muted: #64748b;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --border: #e2e8f0;
}

html, body, [class*="stApp"] {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC", "Space Grotesk", "Avenir Next", "Helvetica Neue", sans-serif;
    color: var(--ink);
}

.stApp {
    background: #ffffff;
}

.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    letter-spacing: -0.02em;
    color: var(--ink);
}

h1 {
    font-weight: 700;
    font-size: 2.1rem;
}

h2 {
    font-weight: 600;
    font-size: 1.6rem;
}

h3 {
    font-weight: 600;
    font-size: 1.3rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 999px;
    padding: 6px 14px;
    color: var(--muted);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(15, 118, 110, 0.12);
    color: var(--brand);
    border: 1px solid rgba(15, 118, 110, 0.25);
}

.stButton > button,
.stFormSubmitButton > button {
    background: var(--brand) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 10px 20px rgba(15, 118, 110, 0.18) !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #0d5f58 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within {
    box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18) !important;
    border-color: rgba(15, 118, 110, 0.45) !important;
}

.stAlert {
    border-radius: 12px !important;
}

/* App-level theming fixes */
html, body {
    background: #ffffff !important;
    background-attachment: fixed !important;
}

.stApp {
    background: #ffffff !important;
    background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"] {
    background: #ffffff !important;
    background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > .main > div {
    background: transparent !important;
}

.block-container {
    background: transparent !important;
}

[data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"],
[data-testid="stAppViewContainer"] section,
[data-testid="stAppViewContainer"] .block-container {
    background: transparent !important;
}


[data-testid="stAppViewContainer"] * {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC", "Space Grotesk", "Avenir Next", "Helvetica Neue", sans-serif !important;
}

/* Top toolbar / header */
[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}


/* 标题强调样式 */
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    position: relative;
    padding-left: 10px;
}

.stMarkdown h2::before,
.stMarkdown h3::before,
.stMarkdown h4::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    background: var(--brand);
    border-radius: 999px;
}

/* 提示卡片统一颜色 */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid rgba(15, 118, 110, 0.15) !important;
}

.stAlert[data-baseweb="notification"] {
    background: rgba(15, 118, 110, 0.08) !important;
    color: var(--ink) !important;
}

/* 错误提示使用更柔和的红 */
.stAlert[role="alert"] {
    background: rgba(239, 68, 68, 0.08) !important;
    border-color: rgba(239, 68, 68, 0.25) !important;
}

/* 信息提示稍微降噪 */
.stInfo, .stSuccess {
    border-left: 4px solid var(--brand) !important;
}

/* 覆盖Streamlit所有可能的选中单元格样式 - 最高优先级 */
.stDataFrame td,
.stDataFrame tr,
.stDataFrame table {
    --dataframe__cell--selected-background-color: rgba(15, 118, 110, 0.3) !important;
    --dataframe__cell--selected-border-color: rgba(15, 118, 110, 0.7) !important;
}

/* 直接覆盖单元格的所有选中、聚焦、激活状态 */
.stDataFrame td:focus,
.stDataFrame td:active,
.stDataFrame td[data-selected="true"],
.stDataFrame td:focus-within {
    background-color: rgba(15, 118, 110, 0.3) !important;
    border: 2px solid rgba(15, 118, 110, 0.7) !important;
    box-shadow: none !important;
    outline: none !important;
    -webkit-tap-highlight-color: transparent !important;
}

/* 处理悬停状态 */
.stDataFrame td:hover {
    background-color: rgba(15, 118, 110, 0.2) !important;
    border-color: rgba(15, 118, 110, 0.5) !important;
}

/* 确保表头样式不受影响 */
.stDataFrame th {
    background-color: #eef2f7 !important;
}

/* 覆盖Streamlit内部样式 - 确保选中状态是蓝色 */
[data-testid="stDataFrame"] td:focus,
[data-testid="stDataFrame"] td:active,
[data-testid="stDataFrame"] td[data-selected="true"] {
    background-color: rgba(15, 118, 110, 0.3) !important;
    border: 2px solid rgba(15, 118, 110, 0.7) !important;
}

/* 增强悬停效果 */
[data-testid="stDataFrame"] td:hover {
    background-color: rgba(15, 118, 110, 0.2) !important;
    border-color: rgba(15, 118, 110, 0.5) !important;
}

/* 重置任何可能的默认选中样式 */
* {
    --primary-color: #0f766e !important;
    --secondary-color: #0f766e !important;
    --accent-color: #0f766e !important;
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

/* 搜索建议列表样式 */
div[data-testid="stRadio"] > div {
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 8px;
    background: #ffffff;
    max-height: 180px;
    overflow-y: auto;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

div[data-testid="stRadio"] label {
    margin: 2px 0;
}




/* 创建群组按钮样式 */
button[title="创建新群组"] {
    background: transparent !important;
    color: #000000 !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 6px !important;
    font-size: 20px !important;
    line-height: 1 !important;
}
button[title="创建新群组"]:hover,
button[title="创建新群组"]:active,
button[title="创建新群组"]:focus {
    background: transparent !important;
    color: #000000 !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
button[title="创建新群组"] * {
    color: #000000 !important;
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
        # 初始化用户ID列表的状态
        if 'user_id_input' not in st.session_state:
            st.session_state.user_id_input = ""
        
        # 创建群组弹窗
        @st.dialog("➕ 创建新群组")
        def create_group_dialog():
            st.subheader("📝 创建新群组")
            
            # 搜索用户功能
            with st.container(border=True):
                st.subheader("🔍 搜索用户")
                search_query = st.text_input(
                    "输入用户名首字母自动推荐",
                    key="search_users_sidebar"
                )
                
                suggested_users = []
                if search_query.strip():
                    try:
                        response = requests.get(
                            f"{API}/users/search",
                            params={"name": search_query}
                        )
                        if response.status_code == 200:
                            users = response.json()
                            suggested_users = users
                            if not suggested_users:
                                st.info("未找到匹配的用户")
                        else:
                            st.error(f"搜索失败: {response.text}")
                    except Exception as e:
                        st.error(f"搜索出错: {str(e)}")
                
                if suggested_users:
                    options = {
                        f"{u['name']} (ID: {u['id']})": u for u in suggested_users
                    }
                    st.caption("推荐用户")
                    selected_label = st.radio(
                        "推荐用户",
                        options=list(options.keys()),
                        key="search_users_suggestions",
                        label_visibility="collapsed"
                    )
                    found_user = options[selected_label]
                    
                    with st.container(border=True):
                        st.subheader("👤 用户信息")
                        st.markdown(f"**用户名:** {found_user['name']}")
                        st.markdown(f"**用户ID:** {found_user['id']}")
                        st.markdown(f"**公开信息:** {found_user.get('public_info', '无')}")
                        
                        add_clicked = st.button(
                            "➕ 添加到群组列表",
                            key=f"add_user_{found_user['id']}_sidebar"
                        )
                        if add_clicked:
                            current_input = st.session_state.get('user_id_input', '')
                            user_id_str = str(found_user['id'])
                            if user_id_str in current_input.split(','):
                                st.warning(f"用户ID {found_user['id']} 已经在列表中")
                            else:
                                if current_input:
                                    new_input = f"{current_input},{found_user['id']}"
                                else:
                                    new_input = str(found_user['id'])
                                st.session_state.user_id_input = new_input
                                st.success(f"✅ 已添加用户ID {found_user['id']} 到列表中")
                                st.rerun()
            
            st.divider()
            st.subheader("📋 已选择用户")
            
            # 当前用户ID列表
            current_ids_input = st.session_state.get('user_id_input', '')
            
            # 显示当前已添加的用户
            if current_ids_input:
                user_ids_list = [id.strip() for id in current_ids_input.split(',') if id.strip()]
                st.write(f"**已选择 {len(user_ids_list)} 个用户:**")
                
                # 为每个用户显示信息
                for idx, user_id in enumerate(user_ids_list):
                    col_user, col_delete = st.columns([4, 1])
                    with col_user:
                        try:
                            user_response = requests.get(f"{API}/users/{user_id}")
                            if user_response.status_code == 200:
                                user_info = user_response.json()
                                # 标记当前用户
                                is_self = str(user_id) == str(user['id'])
                                self_mark = " (您)" if is_self else ""
                                st.write(f"{idx+1}. {user_info['name']} (ID: {user_id}){self_mark}")
                            else:
                                st.write(f"{idx+1}. 未知用户 (ID: {user_id})")
                        except Exception:
                            st.write(f"{idx+1}. 用户ID: {user_id}")
                    
                    with col_delete:
                        # 删除按钮 - 自己也可以删除
                        delete_clicked = st.button("❌", key=f"delete_user_{user_id}_{idx}")
                        if delete_clicked:
                            # 从列表中删除这个ID
                            ids_list = current_ids_input.split(',')
                            filtered_ids = []
                            for id_str in ids_list:
                                id_str_clean = id_str.strip()
                                if id_str_clean and id_str_clean != user_id:
                                    filtered_ids.append(id_str_clean)
                            # 重新组合成字符串
                            new_ids_input = ','.join(filtered_ids)
                            st.session_state.user_id_input = new_ids_input
                            
                            # 如果是删除自己，给出特殊提示
                            is_self = str(user_id) == str(user['id'])
                            if is_self:
                                st.success(f"✅ 已移除您自己 (ID: {user_id})")
                            else:
                                st.success(f"✅ 已移除用户ID {user_id}")
                            st.rerun()
            else:
                st.info("👆 请搜索用户并添加到列表，或直接输入用户ID")
            
            # 用户ID输入框
            st.write("### 用户ID列表")
            user_id_input = st.text_input(
                "输入用户ID（用逗号分隔，如：1,2,3）",
                value=current_ids_input,
                key="user_id_input_widget",
                help="可以直接在这里输入或修改用户ID，用逗号分隔"
            )
            
            # 清空按钮
            clear_clicked = st.button("🗑️ 清空列表", key="clear_list_button_sidebar")
            if clear_clicked:
                st.session_state.user_id_input = ""
                st.success("✅ 已清空用户列表")
                st.rerun()
            
            st.divider()
            st.subheader("📝 创建群组")

            # 使用表单包装创建群组功能
            with st.form(key="create_group_final_form"):
                group_name = st.text_input("群组名称", placeholder="输入新群组的名称")
                
                # 动态计算当前选择的用户
                current_ids_input = st.session_state.get('user_id_input', '')
                user_ids_list = [id.strip() for id in current_ids_input.split(',') if id.strip()]
                
                # 检查自己是否在列表中
                self_in_list = str(user['id']) in user_ids_list
                
                # 显示当前选择的用户 - 动态更新
                if user_ids_list:
                    # 计算其他用户数量（不包括自己）
                    other_users_count = 0
                    for user_id in user_ids_list:
                        if str(user_id) != str(user['id']):
                            other_users_count += 1
                    
                    # 总用户数 = 其他用户数 + （如果自己在列表中则+1）
                    total_users_count = other_users_count + (1 if self_in_list else 0)
                    
                    if self_in_list:
                        st.info(f"当前已选择 {other_users_count} 位其他用户 + 您自己（自动添加）= 总共 {total_users_count} 位成员")
                    else:
                        st.info(f"当前已选择 {other_users_count} 位其他用户 + 您自己（自动添加）= 总共 {total_users_count + 1} 位成员")
                else:
                    # 如果列表为空
                    st.info("当前已选择 0 位其他用户 + 您自己（自动添加）= 总共 1 位成员")
                
                # 验证提示 - 根据是否包含自己来调整验证逻辑
                if self_in_list:
                    # 如果列表中包含自己，需要至少1个其他用户
                    if len([uid for uid in user_ids_list if str(uid) != str(user['id'])]) < 1:
                        st.warning("⚠️ 请至少添加一个其他用户才能创建群组")
                    else:
                        st.success("✅ 已满足创建群组条件")
                else:
                    # 如果列表中没有自己，需要添加至少1个其他用户，且自己会被自动添加
                    if len(user_ids_list) < 1:
                        st.warning("⚠️ 请至少添加一个其他用户才能创建群组")
                    else:
                        st.success("✅ 已满足创建群组条件（您自己会自动加入）")
                
                # 提交按钮
                create_clicked = st.form_submit_button("✅ 创建群组", use_container_width=True)
                
                if create_clicked:
                    if not group_name.strip():
                        st.error("请输入群组名称")
                    else:
                        # 收集用户ID
                        user_ids = set()
                        
                        # 从会话状态中解析用户ID
                        current_input = st.session_state.get('user_id_input', '')
                        if current_input.strip():
                            try:
                                ids_list = [id.strip() for id in current_input.split(',') if id.strip()]
                                for user_id_str in ids_list:
                                    if user_id_str.isdigit():
                                        user_ids.add(int(user_id_str))
                                    else:
                                        st.error(f"用户ID格式错误: {user_id_str} 不是有效数字")
                                        break
                            except Exception as e:
                                st.error(f"解析用户ID时出错: {str(e)}")
                                user_ids = set()
                        
                        # 确保当前用户在列表中（无论是否被删除，创建群组时都会自动添加自己）
                        user_ids.add(user['id'])
                        
                        # 验证 - 实时显示验证结果
                        other_users_count = len([uid for uid in user_ids if str(uid) != str(user['id'])])
                        if other_users_count < 1:
                            st.error("请至少添加一个其他用户")
                        else:
                            # 显示确认信息
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
                                        st.success("✅ 群组创建成功！")
                                        st.write(f"**群组名称:** {group_data['name']}")
                                        st.write(f"**群组ID:** {group_data['id']}")
                                        st.write(f"**成功添加成员:** {group_data['added_members']} 位")
                                        
                                        if group_data['failed_members'] > 0:
                                            st.warning(f"**添加失败:** {group_data['failed_members']} 位成员")
                                        
                                        # 清理状态
                                        if 'user_id_input' in st.session_state:
                                            del st.session_state.user_id_input
                                        
                                        # 刷新群组信息
                                        if 'user_groups' in st.session_state:
                                            del st.session_state.user_groups
                                        
                                        st.rerun()
                                    else:
                                        error_detail = response.json().get('detail', '创建失败')
                                        st.error(f"❌ 创建群组失败: {error_detail}")
                                except Exception as e:
                                    st.error(f"创建群组出错: {str(e)}")

        # 添加创建群组按钮
        col1, col2 = st.columns([1, 0.1])
        with col1:
            st.subheader("👥 群组详情")
        with col2:
            # 显示创建群组按钮
            if st.button("➕", key="create_group_button", help="创建新群组"):
                create_group_dialog()
        
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
                                
                                # 通过搜索用户名添加成员
                                st.subheader("➕ 添加成员")
                                with st.container(border=True):
                                    st.markdown("**通过用户名搜索添加**")
                                    search_query = st.text_input(
                                        "输入用户名首字母自动推荐",
                                        key="add_member_search_query"
                                    )
                                    
                                    suggested_users = []
                                    if search_query.strip():
                                        try:
                                            response = requests.get(
                                                f"{API}/users/search",
                                                params={"name": search_query}
                                            )
                                            if response.status_code == 200:
                                                users = response.json()
                                                suggested_users = users
                                                if not suggested_users:
                                                    st.info("未找到匹配的用户")
                                            else:
                                                st.error(f"搜索失败: {response.text}")
                                        except Exception as e:
                                            st.error(f"搜索出错: {str(e)}")
                                    
                                    if suggested_users:
                                        options = {
                                            f"{u['name']} (ID: {u['id']})": u for u in suggested_users
                                        }
                                        st.caption("推荐用户")
                                        selected_label = st.radio(
                                            "推荐用户",
                                            options=list(options.keys()),
                                            key="add_member_search_suggestions",
                                            label_visibility="collapsed"
                                        )
                                        found_user = options[selected_label]
                                        
                                        with st.container(border=True):
                                            st.subheader("👤 用户信息")
                                            st.markdown(f"**用户名:** {found_user['name']}")
                                            st.markdown(f"**用户ID:** {found_user['id']}")
                                            st.markdown(f"**公开信息:** {found_user.get('public_info', '无')}")
                                            
                                            add_clicked = st.button(
                                                "➕ 添加到群组",
                                                key=f"add_member_{found_user['id']}_btn"
                                            )
                                            if add_clicked:
                                                try:
                                                    response = requests.post(
                                                        f"{API}/groups/{selected_group[1]}/add_member",
                                                        json={
                                                            "current_user_id": user['id'],
                                                            "user_id": int(found_user['id'])
                                                        }
                                                    )
                                                    if response.status_code == 200:
                                                        st.success("✅ 成员添加成功")
                                                        st.rerun()
                                                    else:
                                                        error_detail = response.json().get('detail', '添加失败')
                                                        st.error(f"❌ 添加成员失败: {error_detail}")
                                                except Exception as e:
                                                    st.error(f"添加成员出错: {str(e)}")
                                                    st.error(
                                                        f"API调用详情: {e.response.text if hasattr(e, 'response') else '无详细信息'}"
                                                    )

                                # 备用入口：手动输入 ID
                                with st.container(border=True):
                                    st.markdown("**手动输入用户ID**")
                                    manual_member_id = st.text_input(
                                        "成员ID",
                                        placeholder="输入要添加的用户ID",
                                        key="add_member_manual_id"
                                    )
                                    add_member_manual_clicked = st.button(
                                        "➕ 添加成员ID",
                                        key="add_member_manual_btn"
                                    )
                                    if add_member_manual_clicked:
                                        if not manual_member_id.strip():
                                            st.error("请输入成员ID")
                                        else:
                                            try:
                                                new_member_id_int = int(manual_member_id.strip())
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
                                                st.error(
                                                    f"API调用详情: {e.response.text if hasattr(e, 'response') else '无详细信息'}"
                                                )

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