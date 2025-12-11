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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 首页", "🔍 搜索用户", "➕ 创建群组", "👥 群组详情", "🎫 使用兑换码", "📝 交易记录"])
    
    # ------------------------
    # 首页（第一个标签页）- 个人信息和群组余额
    # ------------------------
    with tab1:
        # 个人信息卡片
        st.subheader("📋 个人信息")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**用户名**: {user['name']}")
        with col2:
            st.info(f"**用户ID**: {user['id']}")
        if user.get('public_info'):
            st.success(f"**公开信息**: {user['public_info']}")
        
        # 查看用户所在群组和余额
        col1, col2 = st.columns([0.95, 0.05])
        with col1:
            st.subheader("📊 我的群组和余额")
        with col2:
            # 使用无边界按钮（通过CSS实现，仅针对刷新按钮）
            st.markdown("""<style>
            /* 仅针对刷新群组信息按钮的样式 */
            div[data-testid="stButton"]:has(button[aria-label="刷新群组信息"]) {
                background-color: transparent !important;
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
                box-shadow: none !important;
            }
            div[data-testid="stButton"]:has(button[aria-label="刷新群组信息"]) > button {
                background-color: transparent !important;
                border: none !important;
                color: #262730 !important;
                padding: 2px !important;
                width: 48px !important;
                height: 24px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                line-height: 1 !important;
                margin: 0 !important;
            }
            div[data-testid="stButton"]:has(button[aria-label="刷新群组信息"]) > button:hover {
                background-color: rgba(0, 0, 0, 0.05) !important;
            }
            </style>""", unsafe_allow_html=True)
            refresh_clicked = st.button("🔄", key="refresh_groups", help="刷新群组信息")
        
        # 处理刷新逻辑
        if refresh_clicked:
            try:
                response = requests.get(f"{API}/users/{user['id']}/groups")
                if response.status_code == 200:
                    data = response.json()
                    # 更新会话中的群组信息
                    st.session_state.user_groups = data['groups']
                    
                    if data['groups']:
                        # 显示用户的群组列表和余额
                        st.write(f"您好，{data['user_name']}，您加入了 {len(data['groups'])} 个群组：")
                        
                        # 创建DataFrame展示群组信息
                        group_data = []
                        for g in data['groups']:
                            # 获取群组详情以显示总成员数
                            group_detail_response = requests.get(f"{API}/groups/{g['group_id']}")
                            total_members = 0
                            if group_detail_response.status_code == 200:
                                group_detail = group_detail_response.json()
                                total_members = group_detail.get('total_members', 0)
                            
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
                        
                        df = pd.DataFrame(group_data, columns=["群组ID", "群组名称", "我的余额", "总成员数"])
                        st.dataframe(df, use_container_width=True)
                        
                        # 计算总余额
                        total_balance = sum(g['balance'] for g in data['groups'])
                        st.metric("💰 所有群组总余额", f"{total_balance:.2f}")
                    else:
                        st.info("您还没有加入任何群组")
                else:
                    st.error(f"获取群组信息失败: {response.text}")
            except Exception as e:
                st.error(f"获取群组信息出错: {str(e)}")
        else:
            # 直接从会话状态显示群组信息（如果有）
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
                            total_members = group_detail.get('total_members', 0)
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
                
                df = pd.DataFrame(group_data, columns=["群组ID", "群组名称", "我的余额", "总成员数"])
                st.dataframe(df, use_container_width=True)
                
                # 计算总余额
                total_balance = sum(g['balance'] for g in st.session_state.user_groups)
                st.metric("💰 所有群组总余额", f"{total_balance:.2f}")
            else:
                st.info("您还没有加入任何群组")
        
        # ------------------------
        # 搜索用户（第二个标签页）
        # ------------------------
        with tab2:
            st.subheader("🔍 搜索用户")
        
            search_query = st.text_input("输入完整用户名进行精确搜索")
            if st.button("🔍 搜索"):
                if not search_query.strip():
                    st.error("请输入用户名")
                else:
                    try:
                        response = requests.get(f"{API}/users/search", params={"name": search_query})
                        if response.status_code == 200:
                            users = response.json()
                            if users:
                                user = users[0]  # 精确匹配，最多只有一个结果
                                st.success(f"✅ 找到用户")
                                st.json({
                                    "用户ID": user["id"],
                                    "用户名": user["name"],
                                    "公开信息": user.get("public_info", "无")
                                })
                                
                                # 提供添加到选择列表的按钮
                                if st.button(f"➕ 添加 {user['name']} 到群组"):
                                    if 'selected_user_ids' not in st.session_state:
                                        st.session_state.selected_user_ids = []
                                    if user['id'] not in st.session_state.selected_user_ids:
                                        st.session_state.selected_user_ids.append(user['id'])
                                        st.success(f"已添加 {user['name']} 到选择列表")
                                    else:
                                        st.warning(f"{user['name']} 已经在选择列表中")
                            else:
                                st.error(f"❌ 未找到用户名 '{search_query}' 的用户")
                        else:
                            st.error(f"搜索失败: {response.text}")
                    except Exception as e:
                        st.error(f"搜索出错: {str(e)}")
        
        # 随机列出用户功能（测试功能）
        st.subheader("🎲 随机用户（测试功能）")
        
        if st.button("🎲 随机列出10个用户"):
            try:
                # 获取所有用户
                response = requests.get(f"{API}/users")
                if response.status_code == 200:
                    all_users = response.json()
                    if all_users:
                        import random
                        # 随机选择最多10个用户
                        random_users = random.sample(all_users, min(10, len(all_users)))
                        
                        st.success(f"✅ 随机获取了 {len(random_users)} 个用户")
                        
                        # 创建DataFrame展示随机用户信息
                        user_data = []
                        for u in random_users:
                            user_data.append([
                                u['id'],
                                u['name'],
                                u.get('public_info', '无')
                            ])
                        
                        df = pd.DataFrame(user_data, columns=["用户ID", "用户名", "公开信息"])
                        st.dataframe(df, use_container_width=True)
                        
                        # 提供批量添加功能
                        st.write("\n**批量操作**")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("➕ 添加所有到选择列表"):
                                if 'selected_user_ids' not in st.session_state:
                                    st.session_state.selected_user_ids = []
                                added_count = 0
                                for u in random_users:
                                    if u['id'] not in st.session_state.selected_user_ids:
                                        st.session_state.selected_user_ids.append(u['id'])
                                        added_count += 1
                                st.success(f"已添加 {added_count} 个用户到选择列表")
                        with col2:
                            if st.button("🔍 查看完整用户列表"):
                                # 查看所有用户的详细信息
                                full_user_data = []
                                for u in all_users:
                                    full_user_data.append([
                                        u['id'],
                                        u['name'],
                                        u.get('public_info', '无')
                                    ])
                                full_df = pd.DataFrame(full_user_data, columns=["用户ID", "用户名", "公开信息"])
                                st.dataframe(full_df, use_container_width=True)
                                st.info(f"数据库中共有 {len(all_users)} 个用户")
                    else:
                        st.info("数据库中暂无用户")
                else:
                    st.error(f"获取用户列表失败: {response.text}")
            except Exception as e:
                st.error(f"获取用户出错: {str(e)}")
        
        # 显示当前选择的用户列表
        if 'selected_user_ids' in st.session_state and st.session_state.selected_user_ids:
            st.subheader("📋 已选择用户")
            
            # 获取并显示已选择用户的详细信息
            selected_users_info = []
            for user_id in st.session_state.selected_user_ids:
                try:
                    response = requests.get(f"{API}/users/{user_id}")
                    if response.status_code == 200:
                        user_info = response.json()
                        selected_users_info.append({
                            "id": user_info["id"],
                            "name": user_info["name"],
                            "public_info": user_info.get("public_info", "无")
                        })
                except:
                    continue
            
            if selected_users_info:
                users_df = pd.DataFrame(selected_users_info)
                st.dataframe(users_df, use_container_width=True)
                
                # 添加移除用户的功能
                remove_user = st.selectbox(
                    "选择要移除的用户",
                    options=[(user["name"], user["id"]) for user in selected_users_info],
                    format_func=lambda x: x[0],
                    index=None,
                    placeholder="选择要移除的用户..."
                )
                
                if remove_user:
                    if st.button("🗑️ 移除用户"):
                        st.session_state.selected_user_ids.remove(remove_user[1])
                        st.success(f"已从选择列表中移除 {remove_user[0]}")
                        st.rerun()  # 重新运行应用以更新显示
            
            # 添加清空选择的按钮
            if st.button("🗑️ 清空所有选择"):
                del st.session_state.selected_user_ids
                st.success("已清空所有选择")
                st.rerun()
    
    # ------------------------
    # 创建群组（第三个标签页）
    # ------------------------
    with tab3:
        st.subheader("➕ 创建新群组")
        
        with st.form("create_group_form"):
            group_name = st.text_input("群组名称")
            
            # 显示已选中的用户（如果有）
            if 'selected_user_ids' in st.session_state:
                st.write(f"已选择用户: {len(st.session_state.selected_user_ids)} 位")
                # 允许用户在创建群组时直接添加更多用户ID
                additional_user_ids = st.text_input("额外用户ID（用逗号分隔，如：1,2,3）")
            else:
                st.info("请先搜索并选择用户，或使用下面的输入框直接输入用户ID")
                additional_user_ids = st.text_input("用户ID列表（用逗号分隔，如：1,2,3）")
            
            submit = st.form_submit_button("创建群组")
        
        if submit:
            if not group_name.strip():
                st.error("请输入群组名称")
            else:
                # 收集所有用户ID
                user_ids = set()
                
                # 添加已选中的用户ID
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
                
                # 确保当前用户也在群组中
                user_ids.add(user['id'])
                
                if not user_ids:
                    st.error("请至少选择一个用户")
                else:
                    try:
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
                            # 清空选中的用户
                            if 'selected_user_ids' in st.session_state:
                                del st.session_state.selected_user_ids
                            # 刷新群组信息
                            if 'user_groups' in st.session_state:
                                del st.session_state.user_groups
                        else:
                            st.error(f"创建群组失败: {response.json().get('detail', '创建失败')}")
                    except Exception as e:
                        st.error(f"创建群组出错: {str(e)}")
    
    # ------------------------
    # 群组详情（第四个标签页）
    # ------------------------
    with tab4:
        st.subheader("👥 群组详情")
        
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
                        group = response.json()
                        st.write(f"**群组名称**: {group['name']}")
                        st.write(f"**总成员数**: {group.get('total_members', 0)}")
                        
                        st.write("\n**群组成员及余额**")
                        if 'members' in group and group['members']:
                            member_data = []
                            for member in group['members']:
                                # 突出显示当前用户
                                is_current_user = member['user_id'] == user['id']
                                user_name = member.get('user', {}).get('name', '未知用户') if 'user' in member else '未知用户'
                                if is_current_user:
                                    user_name = f"**{user_name} (我)**"
                                
                                # 格式化余额显示
                                balance_str = f"{member['balance']:.2f}"
                                balance_color = "🟢" if member['balance'] >= 0 else "🔴"
                                
                                member_data.append([
                                    member['user_id'],
                                    user_name,
                                    f"{balance_color} {balance_str}"
                                ])
                            
                            member_df = pd.DataFrame(member_data, columns=["用户ID", "用户名", "余额"])
                            st.dataframe(member_df, use_container_width=True)
                        else:
                            st.write("该群组暂无成员")
                except Exception as e:
                    st.error(f"获取群组详情出错: {str(e)}")
        else:
            st.info("您还没有加入任何群组")
    
    # ------------------------
    # 使用兑换码（第五个标签页）
    # ------------------------
    with tab5:
        st.subheader("🎫 使用兑换码")
        
        with st.form("use_code_form"):
            code_input = st.text_input("兑换码", placeholder="请输入管理员提供的兑换码")
            
            # 从用户所在的群组中选择
            if st.session_state.user_groups:
                group_options = [(g['group_name'], g['group_id']) for g in st.session_state.user_groups]
                selected_group = st.selectbox(
                    "选择群组",
                    options=group_options,
                    format_func=lambda x: x[0],
                    index=None,
                    placeholder="选择要增加余额的群组..."
                )
            else:
                st.info("您还没有加入任何群组，无法使用兑换码")
                selected_group = None
            
            submit_code = st.form_submit_button("✨ 兑换")
        
        if submit_code:
            if not code_input.strip():
                st.error("请输入兑换码")
            elif not selected_group:
                st.error("请选择有效的群组")
            else:
                try:
                    # 调用使用兑换码API
                    response = requests.post(
                        f"{API}/codes/use",
                        json={
                            "code": code_input.strip(),
                            "group_id": selected_group[1],
                            "user_id": user['id']  # 从当前登录用户的会话状态中获取用户ID
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"🎉 兑换成功！")
                        st.write(f"增加金额: ¥{result['amount']:.2f}")
                        st.write(f"群组: {selected_group[0]}")
                        st.write(f"当前余额: ¥{result['new_balance']:.2f}")
                        
                        # 更新会话中的群组信息，以便用户看到最新余额
                        if 'user_groups' in st.session_state:
                            for g in st.session_state.user_groups:
                                if g['group_id'] == selected_group[1]:
                                    g['balance'] = result['new_balance']
                    else:
                        st.error(f"❌ 兑换失败: {response.json().get('detail', '兑换码无效或已使用')}")
                except Exception as e:
                    st.error(f"兑换出错: {str(e)}")
    
    # ------------------------
    # 交易记录（第六个标签页）
    # ------------------------
    with tab6:
        st.header("我的付款记录")
        try:
            # 获取用户的交易记录
            response = requests.get(f"{API}/transactions/user/{user['id']}")
            if response.status_code == 200:
                transactions = response.json()
                
                if transactions:
                    # 创建交易记录列表
                    transaction_list = []
                    for transaction in transactions:
                        # 计算当前用户在该交易中的支付金额
                        user_amount = 0
                        for participant in transaction["transaction_participants"]:
                            if participant["user_id"] == user['id']:
                                user_amount = participant["amount"]
                        
                        transaction_list.append({
                            "交易ID": transaction["id"],
                            "交易名称": transaction["name"],
                            "群组名称": transaction["group_name"],
                            "交易总金额": transaction["total_amount"],
                            "我的支付": user_amount,
                            "创建者": transaction["creator"],
                            "创建时间": transaction["created_at"].split("T")[0],
                            "状态": transaction["status"]
                        })
                    
                    # 创建DataFrame并显示
                    df = pd.DataFrame(transaction_list)
                    
                    # 添加样式：根据状态显示不同颜色
                    def highlight_status(row):
                        if row["状态"] == "已完成":
                            return ['background-color: #d4edda'] * len(row)
                        elif row["状态"] == "进行中":
                            return ['background-color: #fff3cd'] * len(row)
                        else:
                            return ['background-color: #f8d7da'] * len(row)
                    
                    styled_df = df.style.apply(highlight_status, axis=1)
                    
                    # 显示总交易次数和总支付金额
                    total_transactions = len(transactions)
                    total_paid = sum(t["我的支付"] for t in transaction_list)
                    
                    col1, col2 = st.columns(2)
                    col1.metric("总交易次数", total_transactions)
                    col2.metric("总支付金额", f"¥{total_paid:.2f}")
                    
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.info("您还没有任何交易记录")
            else:
                st.error("获取交易记录失败")
        except Exception as e:
            st.error(f"获取交易记录时出错: {e}")
    # ==================== 页面化设计结束 ====================