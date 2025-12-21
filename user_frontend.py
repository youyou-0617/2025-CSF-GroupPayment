import streamlit as st
import requests
import pandas as pd
import socket

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

/* 模态弹窗样式 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="用户端 - AA 群组记账", page_icon="👤", layout="centered", initial_sidebar_state="expanded" )

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
        
    # ------------------------
    # 群组详情（第二个标签页）
    # ------------------------
    with tab2:
        # 添加创建群组按钮和弹窗
        col1, col2 = st.columns([1, 0.1])
        with col1:
            st.subheader("👥 群组详情")
        with col2:
            # 显示创建群组按钮
            if st.button("➕", key="create_group_button"):
                st.session_state.create_group_modal = True
        
        # 初始化会话状态
        if 'create_group_modal' not in st.session_state:
            st.session_state.create_group_modal = False
        
        # 创建群组弹窗
        if st.session_state.create_group_modal:
            # 显示半透明背景
            st.markdown('<div class="modal-overlay"></div>', unsafe_allow_html=True)
            
            # 创建一个单独的容器用于模态框
            modal_container = st.container()
            
            with modal_container:
                # 模态框内容
                with st.container(border=True, key="modal_content"):
                    # 标题栏
                    header_col1, header_col2 = st.columns([1, 0.1])
                    with header_col1:
                        st.subheader("➕ 创建新群组")
                    with header_col2:
                        # 关闭按钮
                        if st.button("❌", key="close_modal", use_container_width=True):
                            st.session_state.create_group_modal = False
                            st.rerun()
                    
                    # 搜索用户功能
                    with st.container(border=True):
                        st.subheader("🔍 搜索用户")
                        search_query = st.text_input("输入完整用户名进行精确搜索", key="search_users")
                        
                        if st.button("🔍 搜索", key="search_users_btn"):
                            if not search_query.strip():
                                st.error("请输入用户名")
                            else:
                                try:
                                    response = requests.get(f"{API}/users/search", params={"name": search_query})
                                    if response.status_code == 200:
                                        users = response.json()
                                        if users:
                                            found_user = users[0]  # 精确匹配，最多只有一个结果
                                            st.success(f"✅ 找到用户")
                                            
                                            with st.container(border=True):
                                                st.subheader("👤 用户信息")
                                                st.markdown(f"**用户名:** {found_user['name']}")
                                                st.markdown(f"**用户ID:** {found_user['id']}")
                                                st.markdown(f"**公开信息:** {found_user.get('public_info', '无')}")
                                            
                                            # 添加到群组按钮
                                            if st.button(f"➕ 添加 {found_user['name']} 到群组", key=f"add_user_{found_user['id']}"):
                                                if 'selected_user_ids' not in st.session_state:
                                                    st.session_state.selected_user_ids = []
                                                if found_user['id'] not in st.session_state.selected_user_ids:
                                                    st.session_state.selected_user_ids.append(found_user['id'])
                                                    st.success(f"已添加 {found_user['name']} 到选择列表")
                                                else:
                                                    st.warning(f"{found_user['name']} 已经在选择列表中")
                                        else:
                                            st.error(f"❌ 未找到用户名 '{search_query}' 的用户")
                                    else:
                                        st.error(f"搜索失败: {response.text}")
                                except Exception as e:
                                    st.error(f"搜索出错: {str(e)}")
                    
                    # 创建群组表单
                    with st.form("create_group_form"):
                        group_name = st.text_input("群组名称")
                        
                        # 显示已选择的用户
                        if 'selected_user_ids' in st.session_state and st.session_state.selected_user_ids:
                            st.write(f"已选择用户: {len(st.session_state.selected_user_ids)} 位")
                        else:
                            st.info("请先搜索并选择用户，或使用下面的输入框直接输入用户ID")
                        
                        # 直接输入用户ID
                        additional_user_ids = st.text_input("用户ID列表（用逗号分隔，如：1,2,3）")
                        
                        # 提交和取消按钮
                        submit_col1, submit_col2 = st.columns(2)
                        with submit_col1:
                            submit_button = st.form_submit_button("创建群组")
                        with submit_col2:
                            cancel_button = st.form_submit_button("取消")
                    
                    # 处理取消按钮
                    if cancel_button:
                        st.session_state.create_group_modal = False
                        st.rerun()
                    
                    # 处理表单提交
                    if submit_button:
                        if not group_name.strip():
                            st.error("请输入群组名称")
                        else:
                            # 收集用户ID
                            user_ids = set()
                            
                            # 添加已选中的用户
                            if 'selected_user_ids' in st.session_state:
                                user_ids.update(st.session_state.selected_user_ids)
                            
                            # 添加额外输入的用户ID
                            if additional_user_ids.strip():
                                try:
                                    extra_ids = [int(id.strip()) for id in additional_user_ids.split(',') if id.strip().isdigit()]
                                    user_ids.update(extra_ids)
                                except:
                                    st.error("用户ID格式错误，请使用逗号分隔的数字")
                                    user_ids = set()
                            
                            # 添加当前用户
                            user_ids.add(user['id'])
                            
                            if not user_ids:
                                st.error("请至少选择一个用户")
                            else:
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
                                        st.success(f"群组创建成功！")
                                        st.write(f"群组ID: {group_data['id']}")
                                        st.write(f"群组名称: {group_data['name']}")
                                        st.write(f"成功添加 {group_data['added_members']} 位成员")
                                        
                                        if group_data['failed_members'] > 0:
                                            st.warning(f"{group_data['failed_members']} 位成员添加失败")
                                        
                                        # 清理选择的用户
                                        if 'selected_user_ids' in st.session_state:
                                            del st.session_state.selected_user_ids
                                        
                                        # 刷新群组信息
                                        if 'user_groups' in st.session_state:
                                            del st.session_state.user_groups
                                        
                                        # 关闭弹窗
                                        st.session_state.create_group_modal = False
                                        st.rerun()
                                    else:
                                        st.error(f"创建群组失败: {response.json().get('detail', '创建失败')}")
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
                            st.subheader(f"📊 {group_detail['group_name']} - 群组详情")
                            
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
                                member_data = []
                                for member in members:
                                    # 为每个成员获取余额
                                    member_balance = 0
                                    for g in st.session_state.user_groups:
                                        if g['group_id'] == selected_group[1] and g['member_id'] == member['id']:
                                            member_balance = g['balance']
                                            break
                                    
                                    # 格式化余额显示
                                    balance_str = f"{member_balance:.2f}"
                                    balance_color = "🟢" if member_balance >= 0 else "🔴"
                                    
                                    member_data.append([
                                        member['id'],
                                        member['name'],
                                        f"{balance_color} {balance_str}"
                                    ])
                                
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
                                    transaction_data.append([
                                        t['id'],
                                        t['name'],
                                        f"{t['amount']:.2f}",
                                        t['description'],
                                        t['created_at']
                                    ])
                                
                                transaction_df = pd.DataFrame(transaction_data, columns=["交易ID", "项目名称", "金额", "描述", "创建时间"], index=range(1, len(transaction_data)+1))
                                st.dataframe(transaction_df, use_container_width=True)
                            else:
                                st.info("该群组暂无交易记录")
                        else:
                            st.error(f"获取群组详情失败: {response.text}")
                    except Exception as e:
                        st.error(f"获取群组详情出错: {str(e)}")
            else:
                st.info("您还没有加入任何群组")
    
    # ------------------------
    # 使用兑换码（第三个标签页）
    # ------------------------
    with tab3:
        st.subheader("🎫 使用兑换码")
        with st.form("redeem_form"):
            coupon_code = st.text_input("请输入兑换码")
            submit = st.form_submit_button("使用")
        
        if submit:
            if not coupon_code.strip():
                st.error("请输入兑换码")
            else:
                try:
                    response = requests.post(
                        f"{API}/coupons/redeem",
                        json={"user_id": user['id'], "code": coupon_code}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"兑换成功！您获得了 {data['amount']} 元")
                    else:
                        st.error(f"兑换失败: {response.json().get('detail', '兑换码无效')}")
                except Exception as e:
                    st.error(f"兑换出错: {str(e)}")
    
    # ------------------------
    # 交易记录（第四个标签页）
    # ------------------------
    with tab4:
        st.subheader("📝 交易记录")
        try:
            response = requests.get(f"{API}/users/{user['id']}/transactions")
            if response.status_code == 200:
                data = response.json()
                transactions = data['transactions']
                
                if transactions:
                    transaction_data = []
                    for t in transactions:
                        transaction_data.append([
                            t['id'],
                            t['group_name'],
                            t['name'],
                            f"{t['amount']:.2f}",
                            t['description'],
                            t['created_at']
                        ])
                    
                    df = pd.DataFrame(transaction_data, columns=["交易ID", "群组名称", "项目名称", "金额", "描述", "创建时间"], index=range(1, len(transaction_data)+1))
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("您还没有任何交易记录")
            else:
                st.error(f"获取交易记录失败: {response.text}")
        except Exception as e:
            st.error(f"获取交易记录出错: {str(e)}")
    
    # ------------------------
    # 随机用户（第五个标签页）
    # ------------------------
    with tab5:
        st.subheader("🎲 随机用户")
        st.write("点击按钮随机查看一个用户的公开信息")
        
        if st.button("🎲 随机查看"):
            try:
                response = requests.get(f"{API}/users/random")
                if response.status_code == 200:
                    random_user = response.json()
                    st.success(f"✅ 随机用户信息")
                    
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**用户名:** {random_user['name']}")
                        with col2:
                            st.info(f"**用户ID:** {random_user['id']}")
                        
                        if random_user.get('public_info'):
                            st.success(f"**公开信息:** {random_user['public_info']}")
                        else:
                            st.info("该用户没有设置公开信息")
                else:
                    st.error(f"获取随机用户失败: {response.text}")
            except Exception as e:
                st.error(f"获取随机用户出错: {str(e)}")