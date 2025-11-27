import streamlit as st
import requests
import pandas as pd

# 使用局域网IP地址，允许其他电脑访问
API = "http://10.31.1.192:8001"

st.set_page_config(page_title="用户端 - AA 群组记账", page_icon="👤", layout="centered")

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
    
    # 查看用户所在群组和余额
    st.write("---")
    st.subheader("📊 我的群组和余额")
    
    if st.button("🔄 刷新群组信息"):
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
                except:
                    total_members = 0
                
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
    
    # 用户搜索功能
    st.write("---")
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
    
    # 显示当前选择的用户列表
    if 'selected_user_ids' in st.session_state and st.session_state.selected_user_ids:
        st.write("---")
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
    
    # 创建群组功能（通过搜索）
    st.write("---")
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
                    else:
                        st.error(f"创建群组失败: {response.json().get('detail', '创建失败')}")
                except Exception as e:
                    st.error(f"创建群组出错: {str(e)}")
    
    # 查看特定群组的详细信息
    st.write("---")
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
        
        if selected_group and st.button("👁️ 查看群组详情"):
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
    
    # 使用兑换码功能
    st.write("---")
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
    
    # 查看付款记录
    st.write("---")
    st.subheader("📝 我的付款记录")
    if st.button("🔄 刷新交易记录"):
        try:
            response = requests.get(f"{API}/users/{user['id']}/transactions")
            if response.status_code == 200:
                data = response.json()
                transactions = data['transactions']
                
                if transactions:
                    # 转换为DataFrame进行展示
                    transaction_df = pd.DataFrame(transactions)
                    
                    # 格式化时间
                    if 'created_at' in transaction_df.columns:
                        transaction_df['created_at'] = pd.to_datetime(transaction_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 选择要显示的列
                    display_columns = [
                        'transaction_id', 'group_name', 'description', 'total_amount', 
                        'is_aa', 'is_payer', 'payer_name', 'my_share', 'my_paid', 'created_at'
                    ]
                    
                    # 确保所有列都存在
                    display_columns = [col for col in display_columns if col in transaction_df.columns]
                    
                    # 创建样式函数来高亮显示付款状态
                    def highlight_transactions(val):
                        if val.name == 'my_share':
                            return ['color: blue' if x > 0 else '' for x in val]
                        elif val.name == 'my_paid':
                            return ['color: green' if x > 0 else '' for x in val]
                        elif val.name == 'is_payer':
                            return ['background-color: lightyellow' if x else '' for x in val]
                        return [''] * len(val)
                    
                    # 显示交易记录表格
                    styled_df = transaction_df[display_columns].style.apply(highlight_transactions)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # 计算统计信息
                    total_spent = sum(t['my_paid'] for t in transactions)
                    total_owed = sum(t['my_share'] - t['my_paid'] for t in transactions)
                    
                    st.info(f"累计付款: ¥{total_spent:.2f}")
                    if total_owed > 0:
                        st.warning(f"待付金额: ¥{total_owed:.2f}")
                    else:
                        st.success(f"超付金额: ¥{-total_owed:.2f}")
                else:
                    st.info("暂无交易记录")
            else:
                st.error(f"获取交易记录失败: {response.text}")
        except Exception as e:
            st.error(f"获取交易记录出错: {str(e)}")