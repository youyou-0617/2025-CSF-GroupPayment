import streamlit as st
import requests
import pandas as pd
import socket
import time  # 用于可能的延时处理

# =======================
# 必须最先调用 set_page_config
# =======================
st.set_page_config(
    page_title="用户端 - AA 群组记账",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =======================
# 获取本地 IP 地址
# =======================
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except:
        return "localhost"

API = f"http://{get_local_ip()}:8001"

# =======================
# 自定义 CSS 样式
# =======================
st.markdown("""
<style>
/* DataFrame 选中/聚焦/悬停样式 */
.stDataFrame td:focus,
.stDataFrame td:active,
.stDataFrame td[data-selected="true"] {
    background-color: rgba(0, 123, 255, 0.3) !important;
    border: 2px solid rgba(0, 123, 255, 0.7) !important;
    outline: none !important;
}
.stDataFrame td:hover {
    background-color: rgba(0, 123, 255, 0.2) !important;
}
.stDataFrame th {
    background-color: #f0f2f6 !important;
}

/* 模态框样式 */
div[data-modal="overlay"] {
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    background-color: rgba(0,0,0,0.5) !important; z-index: 9999 !important;
}
div[data-modal="content"] {
    position: fixed !important;
    top: 50% !important; left: 50% !important;
    transform: translate(-50%, -50%) !important;
    background-color: white !important;
    padding: 20px !important; border-radius: 8px !important;
    z-index: 10000 !important; width: 80% !important;
    max-width: 700px !important; max-height: 80vh !important;
    overflow-y: auto !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# =======================
# 初始化会话状态
# =======================
if 'user' not in st.session_state:
    st.session_state.user = None

# =======================
# 登录/注册逻辑
# =======================
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["登录", "注册"])

    # ---------- 登录 ----------
    with tab1:
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
                    response = requests.post(f"{API}/users/login", json={"name": username, "password": password})
                    if response.status_code == 200:
                        st.session_state.user = response.json()
                        st.success(f"登录成功！欢迎回来，{username}")
                        st.rerun()
                    else:
                        st.error(f"登录失败: {response.json().get('detail','用户名或密码错误')}")
                except Exception as e:
                    st.error(f"登录出错: {str(e)}")

    # ---------- 注册 ----------
    with tab2:
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
                    response = requests.post(
                        f"{API}/users/register",
                        json={"name": username, "password": password, "public_info": public_info}
                    )
                    if response.status_code == 200:
                        st.session_state.user = response.json()
                        st.success(f"注册成功！欢迎，{username}")
                        st.rerun()
                    else:
                        st.error(f"注册失败: {response.json().get('detail','注册失败')}")
                except Exception as e:
                    st.error(f"注册出错: {str(e)}")

# =======================
# 登录后的主页面
# =======================
else:
    user = st.session_state.user
    st.title(f"👤 欢迎回来，{user['name']}")
    
    # 登出按钮
    if st.button("退出登录"):
        st.session_state.user = None
        if 'user_groups' in st.session_state:
            del st.session_state.user_groups
        st.rerun()
    
    # 获取用户群组信息
    if 'user_groups' not in st.session_state:
        try:
            response = requests.get(f"{API}/users/{user['id']}/groups")
            if response.status_code == 200:
                st.session_state.user_groups = response.json().get('groups', [])
            else:
                st.session_state.user_groups = []
        except:
            st.session_state.user_groups = []

    # =======================
    # 页面化导航
    # =======================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 首页", "👥 群组详情", "🎫 使用兑换码", "📝 交易记录", "🎲 随机用户"])

    # ---------- 首页 ----------
    with tab1:
        st.subheader("📋 个人信息")
        col1, col2, col3 = st.columns(3)
        col1.metric("👤 用户名", user['name'])
        col2.metric("🆔 用户ID", user['id'])
        col3.metric("ℹ️ 公开信息", user.get('public_info', '无'))

        st.divider()
        st.subheader("📊 我的群组和余额")
        if st.session_state.user_groups:
            for g in st.session_state.user_groups:
                balance_color = "🟢" if g['balance'] >= 0 else "🔴"
                st.info(f"{g['group_name']} ({g['group_id']}): {balance_color} {g['balance']:.2f}")
            total_balance = sum(g['balance'] for g in st.session_state.user_groups)
            st.success(f"💰 所有群组总余额: {total_balance:.2f}")
        else:
            st.info("您还没有加入任何群组")
        
        if st.button("🔄 刷新"):
            try:
                response = requests.get(f"{API}/users/{user['id']}/groups")
                if response.status_code == 200:
                    st.session_state.user_groups = response.json().get('groups', [])
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"刷新失败: {e}")

    # ---------- 群组详情（第二个标签页） ----------
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
                
                # 搜索用户功能
                with st.container(border=True):
                    st.subheader("🔍 搜索用户")
                    search_query = st.text_input("输入完整用户名进行精确搜索", key="search_users_sidebar")
                    
                    # 使用一个标志来跟踪搜索状态
                    if 'search_triggered' not in st.session_state:
                        st.session_state.search_triggered = False
                    
                    # 搜索按钮
                    if st.button("🔍 搜索", key="search_users_btn_sidebar"):
                        st.session_state.search_triggered = True
                    
                    # 显示搜索结果
                    if st.session_state.get('search_triggered', False):
                        if not search_query.strip():
                            st.error("请输入用户名")
                            st.session_state.search_triggered = False
                        else:
                            try:
                                response = requests.get(f"{API}/users/search", params={"name": search_query})
                                if response.status_code == 200:
                                    users = response.json()
                                    if users:
                                        found_user = users[0]
                                        st.success(f"✅ 找到用户")
                                        
                                        with st.container(border=True):
                                            st.subheader("👤 用户信息")
                                            st.markdown(f"**用户名:** {found_user['name']}")
                                            st.markdown(f"**用户ID:** {found_user['id']}")
                                            st.markdown(f"**公开信息:** {found_user.get('public_info', '无')}")
                                            
                                            # 添加到群组按钮 - 简单的实现
                                            add_clicked = st.button(f"➕ 添加到群组列表", 
                                                                key=f"add_user_{found_user['id']}_sidebar")
                                            
                                            if add_clicked:
                                                current_input = st.session_state.get('user_id_input', '')
                                                
                                                # 检查是否已经添加过这个用户ID
                                                user_id_str = str(found_user['id'])
                                                if user_id_str in current_input.split(','):
                                                    st.warning(f"用户ID {found_user['id']} 已经在列表中")
                                                else:
                                                    # 添加用户ID到列表
                                                    if current_input:
                                                        new_input = f"{current_input},{found_user['id']}"
                                                    else:
                                                        new_input = str(found_user['id'])
                                                    
                                                    # 更新会话状态
                                                    st.session_state.user_id_input = new_input
                                                    st.success(f"✅ 已添加用户ID {found_user['id']} 到列表中")
                                                    # 重置搜索状态
                                                    st.session_state.search_triggered = False
                                                    st.rerun()
                                    else:
                                        st.error(f"❌ 未找到用户名 '{search_query}' 的用户")
                                        st.session_state.search_triggered = False
                                else:
                                    st.error(f"搜索失败: {response.text}")
                                    st.session_state.search_triggered = False
                            except Exception as e:
                                st.error(f"搜索出错: {str(e)}")
                                st.session_state.search_triggered = False
                
                # 用户ID输入框和操作按钮
                st.write("---")
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
                            except:
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
                
                # 操作按钮行
                col_ops1, col_ops2 = st.columns(2)
                with col_ops1:
                    # 添加自己按钮
                    add_self_clicked = st.button("➕ 添加自己", key="add_self_button_sidebar")
                    if add_self_clicked:
                        current_input = st.session_state.get('user_id_input', '')
                        if str(user['id']) in current_input.split(','):
                            st.warning("您已经在列表中")
                        else:
                            if current_input:
                                new_input = f"{current_input},{user['id']}"
                            else:
                                new_input = str(user['id'])
                            st.session_state.user_id_input = new_input
                            st.success(f"✅ 已添加自己 (ID: {user['id']}) 到列表中")
                            st.rerun()
                
                with col_ops2:
                    # 清空按钮
                    clear_clicked = st.button("🗑️ 清空列表", key="clear_list_button_sidebar")
                    if clear_clicked:
                        st.session_state.user_id_input = ""
                        st.success("✅ 已清空用户列表")
                        st.rerun()
                
                # 创建群组表单
                st.write("---")
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
                            st.info(f"当前已选择 {other_users_count} 位其他用户 + 您自己 = 总共 {total_users_count} 位成员")
                        else:
                            st.info(f"当前已选择 {other_users_count} 位其他用户 + 您自己（未添加）= 总共 {total_users_count + 1} 位成员")
                    else:
                        # 如果列表为空
                        st.info("当前已选择 0 位其他用户 + 您自己（未添加）= 总共 1 位成员")
                    
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
                                            st.success(f"✅ 群组创建成功！")
                                            st.write(f"**群组名称:** {group_data['name']}")
                                            st.write(f"**群组ID:** {group_data['id']}")
                                            st.write(f"**成功添加成员:** {group_data['added_members']} 位")
                                            
                                            if group_data['failed_members'] > 0:
                                                st.warning(f"**添加失败:** {group_data['failed_members']} 位成员")
                                            
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
                group_options = [(g.get('group_name', g.get('name', '未知群组')), g['group_id']) for g in st.session_state.user_groups]
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
                        group_detail = response.json()
                        
                        # 获取群组名称
                        group_name = group_detail.get('group_name') or group_detail.get('name', '未知群组')
                        st.subheader(f"📊 {group_name} - 群组详情")
                        
                        # 显示群组信息
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**群组ID:** {group_detail.get('id', '未知')}")
                        with col2:
                            st.info(f"**创建时间:** {group_detail.get('created_at', '未知')}")
                        
                        # 显示成员列表
                        st.subheader("👥 成员列表")
                        members = group_detail.get('members', [])
                        if members:
                            member_data = []
                            for member in members:
                                member_name = member.get('name', f"用户{member.get('id', '未知')}")
                                member_id = member.get('id', '未知')

                                # 为每个成员获取余额
                                member_balance = 0
                                for g in st.session_state.user_groups:
                                    if g['group_id'] == selected_group[1] and g.get('member_id') == member_id:
                                        member_balance = g.get('balance', 0)
                                        break
                                
                                balance_str = f"{member_balance:.2f}"
                                balance_color = "🟢" if member_balance >= 0 else "🔴"
                                member_data.append([member_id, member_name, f"{balance_color} {balance_str}"])
                            
                            member_df = pd.DataFrame(member_data, columns=["成员ID", "成员名称", "余额"], index=range(1, len(member_data)+1))
                            st.dataframe(member_df, use_container_width=True)
                        else:
                            st.info("该群组暂无成员")
                        
                        # 显示交易记录
                        st.subheader("📝 交易记录")
                        transactions = group_detail.get('transactions', [])
                        if transactions:
                            transaction_data = []
                            for t in transactions:
                                t_name = t.get('name', f"交易{t.get('id', '')}")
                                t_amount = t.get('amount', 0)
                                t_desc = t.get('description', '')
                                t_created = t.get('created_at', '')
                                t_id = t.get('id', '')
                                transaction_data.append([t_id, t_name, f"{t_amount:.2f}", t_desc, t_created])
                            
                            transaction_df = pd.DataFrame(transaction_data, columns=["交易ID", "项目名称", "金额", "描述", "创建时间"], index=range(1, len(transaction_data)+1))
                            st.dataframe(transaction_df, use_container_width=True)
                        else:
                            st.info("该群组暂无交易记录")
                        
                    except Exception as e:
                        st.error(f"获取群组详情出错: {str(e)}")
            else:
                st.info("您还没有加入任何群组")



    # ---------- 兑换码（第三个标签页） ----------
    with tab3:
        st.subheader("🎫 使用兑换码")
        code = st.text_input("请输入兑换码", max_chars=10, placeholder="例如: ABC1234567")
        if st.button("💡 兑换"):
            if not code.strip():
                st.error("请输入兑换码")
            else:
                try:
                    response = requests.post(f"{API}/redeem_code", json={"code": code, "user_id": user['id']})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"兑换成功！获得: {data['amount']} 元")
                        # 刷新用户信息
                        response = requests.get(f"{API}/users/{user['id']}")
                        if response.status_code == 200:
                            st.session_state.user = response.json()
                            st.rerun()
                    else:
                        st.error(f"兑换失败: {response.json().get('detail','兑换码无效')}")
                except Exception as e:
                    st.error(f"兑换出错: {str(e)}")

    # ---------- 交易记录（第四个标签页） ----------
    with tab4:
        st.subheader("📝 交易记录")
        try:
            response = requests.get(f"{API}/transactions", params={"user_id": user['id']})
            if response.status_code == 200:
                transactions = response.json()
                if transactions:
                    df = pd.DataFrame(transactions)
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df = df.sort_values(by='timestamp', ascending=False)
                    df['交易类型'] = df['transaction_type'].map({'charge':'充值','payment':'付款','redeem':'兑换'})
                    display_columns = ['timestamp','transaction_id','amount','交易类型']
                    df = df.rename(columns={'timestamp':'交易时间','transaction_id':'交易ID','amount':'金额','description':'描述'})
                    df['金额'] = df['金额'].apply(lambda x: f"¥{x:.2f}")
                    st.dataframe(df[display_columns], use_container_width=True)
                else:
                    st.info("暂无交易记录")
            else:
                st.error(f"获取交易记录失败: {response.text}")
        except Exception as e:
            st.error(f"获取交易记录出错: {str(e)}")

    # ---------- 随机用户（第五个标签页） ----------
    with tab5:
        st.subheader("🎲 随机用户")
        if st.button("🎲 获取随机用户"):
            try:
                response = requests.get(f"{API}/users/random")
                if response.status_code == 200:
                    random_user = response.json()
                    st.success("✅ 获取随机用户成功")
                    st.markdown(f"**用户名:** {random_user['name']}")
                    st.markdown(f"**用户ID:** {random_user['id']}")
                    if random_user.get('public_info'):
                        st.markdown(f"**公开信息:** {random_user['public_info']}")
                else:
                    st.error(f"获取随机用户失败: {response.text}")
            except Exception as e:
                st.error(f"获取随机用户出错: {str(e)}")
