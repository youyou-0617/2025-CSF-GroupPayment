import streamlit as st
import requests
import pandas as pd

# 使用局域网IP地址，允许其他电脑访问
API = "http://10.31.2.50:8001"

st.set_page_config(page_title="管理员端 - AA 群组记账", page_icon="🔧", layout="wide")

# 初始化会话状态
if 'admin' not in st.session_state:
    st.session_state.admin = None

# 管理员登录页面
def admin_login():
    st.title("🔧 管理员登录")
    st.write("请使用管理员账号登录")
    
    with st.form("admin_login_form"):
        username = st.text_input("管理员用户名")
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
                        # 检查用户是否是管理员（基于用户名）
                        if username.lower() == 'admin' or 'admin' in str(user_data.get('public_info', '')).lower():
                            st.session_state.admin = user_data
                            st.success(f"登录成功！欢迎，{username}")
                            # 刷新页面显示登录后的内容
                            st.rerun()
                        else:
                            st.error("您不是管理员，无权访问")
                else:
                    st.error(f"登录失败: {response.json().get('detail', '用户名或密码错误')}")
            except Exception as e:
                st.error(f"登录出错: {str(e)}")

# 管理员主页面
def admin_dashboard():
    admin = st.session_state.admin
    st.title(f"🔧 管理员控制台")
    
    # 登出按钮
    if st.button("退出登录"):
        st.session_state.admin = None
        st.rerun()
    
    # 页面导航
    tabs = ["🎫 生成兑换码", "👥 用户与群组管理", "📊 兑换码管理", "💰 交易管理"]
    selected_tab = st.sidebar.radio("导航菜单", tabs)
    
    # 生成兑换码功能
    if selected_tab == "🎫 生成兑换码":
        st.write("---")
        st.subheader("🎫 生成兑换码")
        
        with st.form("create_code_form"):
            amount = st.number_input("兑换金额", min_value=0.01, step=0.01, format="%.2f")
            submit_code = st.form_submit_button("生成兑换码")
        
        if submit_code:
            if amount <= 0:
                st.error("请输入有效的金额")
            else:
                try:
                    # 调用生成兑换码API
                    response = requests.post(
                        f"{API}/codes",
                        json={"amount": amount}
                    )
                    
                    if response.status_code == 200:
                        code_data = response.json()
                        st.success(f"🎉 兑换码生成成功！")
                        
                        # 显示兑换码信息
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**完整兑换码:**")
                            st.code(code_data['code'], language="")  # 显示完整兑换码而不是前缀
                            st.write(f"**兑换码前缀:** {code_data['code_prefix']}")  # 额外显示前缀
                        with col2:
                            st.write(f"**金额:** ¥{code_data['amount']:.2f}")
                            st.write(f"**生成时间:** {code_data['created_at']}")
                            st.write(f"**状态:** {'未使用' if not code_data['is_used'] else '已使用'}")
                            st.write(f"**有效期至:** {code_data.get('expires_at', '永久有效')}")
                        
                        # 添加复制按钮（Streamlit原生支持）
                        st.info("💡 提示：点击上方完整兑换码的代码块可一键复制")
                        st.warning("⚠️ 重要：请妥善保管兑换码，只在创建时显示一次！")
                    else:
                        st.error(f"❌ 生成失败: {response.json().get('detail', '生成兑换码失败')}")
                except Exception as e:
                    st.error(f"生成出错: {str(e)}")
    
    # 用户与群组管理
    elif selected_tab == "👥 用户与群组管理":
        st.write("---")
        st.subheader("👥 用户与群组管理")
        
        # 子选项卡
        sub_tabs = ["查看所有用户", "查看所有群组"]
        sub_selected = st.selectbox("选择操作", sub_tabs)
        
        # 查看所有用户
        if sub_selected == "查看所有用户":
            st.write("### 📋 所有用户列表")
            
            if st.button("🔄 获取用户列表"):
                try:
                    response = requests.get(f"{API}/users")
                    if response.status_code == 200:
                        users = response.json()
                        
                        if users:
                            # 转换为DataFrame进行展示
                            users_df = pd.DataFrame(users)
                            
                            # 格式化时间
                            if 'created_at' in users_df.columns:
                                users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # 选择要显示的列
                            display_columns = ['id', 'name', 'public_info', 'created_at']
                            
                            # 确保所有列都存在
                            display_columns = [col for col in display_columns if col in users_df.columns]
                            
                            # 显示用户表格
                            st.dataframe(users_df[display_columns], use_container_width=True)
                            
                            # 显示统计信息
                            st.write(f"**总共 {len(users_df)} 个用户**")
                        else:
                            st.info("暂无用户数据")
                    else:
                        st.error(f"获取用户列表失败: {response.text}")
                except Exception as e:
                    st.error(f"获取出错: {str(e)}")
            
            # 用户详情查询
            st.write("### 🔍 用户详情查询")
            user_id = st.number_input("输入用户ID", min_value=1, step=1)
            if st.button("查询用户详情"):
                try:
                    # 获取用户基本信息
                    user_response = requests.get(f"{API}/users/{user_id}")
                    if user_response.status_code == 200:
                        user = user_response.json()
                        
                        st.write("#### 用户基本信息")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**用户ID:** {user['id']}")
                            st.write(f"**用户名:** {user['name']}")
                        with col2:
                            st.write(f"**公开信息:** {user['public_info']}")
                            if 'created_at' in user:
                                st.write(f"**创建时间:** {pd.to_datetime(user['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # 获取用户余额
                        balance_response = requests.get(f"{API}/users/{user_id}/balance")
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            st.write(f"**当前余额:** ¥{balance_data['balance']:.2f}")
                        
                        # 获取用户所在群组
                        groups_response = requests.get(f"{API}/users/{user_id}/groups")
                        if groups_response.status_code == 200:
                            groups_data = groups_response.json()
                            if groups_data['groups']:
                                st.write("#### 用户所在群组")
                                groups_df = pd.DataFrame(groups_data['groups'])
                                st.dataframe(groups_df[['group_id', 'group_name', 'balance']], use_container_width=True)
                            else:
                                st.write("该用户未加入任何群组")
                    else:
                        st.error(f"获取用户信息失败: {user_response.text}")
                except Exception as e:
                    st.error(f"查询出错: {str(e)}")
        
        # 查看所有群组
        elif sub_selected == "查看所有群组":
            st.write("### 📋 所有群组列表")
            
            if st.button("🔄 获取群组列表"):
                try:
                    response = requests.get(f"{API}/groups")
                    if response.status_code == 200:
                        groups = response.json()
                        
                        if groups:
                            # 转换为DataFrame进行展示
                            groups_df = pd.DataFrame(groups)
                            
                            # 显示群组表格
                            st.dataframe(groups_df[['id', 'name']], use_container_width=True)
                            
                            # 显示统计信息
                            st.write(f"**总共 {len(groups_df)} 个群组**")
                        else:
                            st.info("暂无群组数据")
                    else:
                        st.error(f"获取群组列表失败: {response.text}")
                except Exception as e:
                    st.error(f"获取出错: {str(e)}")
            
            # 群组详情查询
            st.write("### 🔍 群组详情查询")
            group_id = st.number_input("输入群组ID", min_value=1, step=1)
            if st.button("查询群组详情"):
                try:
                    response = requests.get(f"{API}/groups/{group_id}")
                    if response.status_code == 200:
                        group = response.json()
                        
                        st.write("#### 群组基本信息")
                        st.write(f"**群组ID:** {group['id']}")
                        st.write(f"**群组名称:** {group['name']}")
                        
                        if 'members' in group and group['members']:
                            st.write("#### 群组成员")
                            members_data = []
                            for member in group['members']:
                                if 'user' in member:
                                    members_data.append({
                                        '用户ID': member['user_id'],
                                        '用户名': member['user']['name'],
                                        '余额': member['balance'] if 'balance' in member else 0
                                    })
                            
                            members_df = pd.DataFrame(members_data)
                            st.dataframe(members_df, use_container_width=True)
                            st.write(f"**总共 {len(members_df)} 个成员**")
                        else:
                            st.write("该群组暂无成员")
                    else:
                        st.error(f"获取群组信息失败: {response.text}")
                except Exception as e:
                    st.error(f"查询出错: {str(e)}")
    
    # 兑换码管理
    elif selected_tab == "📊 兑换码管理":
        st.write("---")
        st.subheader("📊 兑换码管理")
        
        # 查看个人生成的兑换码
        st.write("### 🎫 我生成的兑换码")
        
        if st.button("🔄 查看我的兑换码"):
            try:
                response = requests.get(f"{API}/codes")
                if response.status_code == 200:
                    codes = response.json()
                    
                    if codes:
                        # 转换为DataFrame进行展示
                        code_df = pd.DataFrame(codes)
                        
                        # 格式化时间
                        if 'created_at' in code_df.columns:
                            code_df['created_at'] = pd.to_datetime(code_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        if 'used_at' in code_df.columns:
                            code_df['used_at'] = pd.to_datetime(code_df['used_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        if 'expires_at' in code_df.columns:
                            code_df['expires_at'] = pd.to_datetime(code_df['expires_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 选择要显示的列
                        display_columns = [
                            'id', 'code_prefix', 'amount', 'is_used', 'created_at',
                            'used_at', 'expires_at'
                        ]
                        
                        # 确保所有列都存在
                        display_columns = [col for col in display_columns if col in code_df.columns]
                        
                        # 显示兑换码表格
                        st.dataframe(code_df[display_columns], use_container_width=True)
                        
                        # 显示统计信息
                        total_codes = len(code_df)
                        used_codes = code_df['is_used'].sum() if 'is_used' in code_df.columns else 0
                        unused_codes = total_codes - used_codes
                        total_amount = code_df['amount'].sum()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("总数量", total_codes)
                        with col2:
                            st.metric("已使用", used_codes)
                        with col3:
                            st.metric("未使用", unused_codes)
                        with col4:
                            st.metric("总金额", f"¥{total_amount:.2f}")
                    else:
                        st.info("您还没有生成任何兑换码")
                else:
                    st.error(f"获取兑换码失败: {response.text}")
            except Exception as e:
                st.error(f"获取出错: {str(e)}")
        
        # 查看已使用的兑换码
        st.write("---")
        st.subheader("📊 兑换码使用统计")
        
        if st.button("🔄 查看使用统计"):
            try:
                response = requests.get(f"{API}/codes/used")
                if response.status_code == 200:
                    used_codes = response.json()
                    
                    if used_codes:
                        # 转换为DataFrame进行展示
                        code_df = pd.DataFrame(used_codes)
                        
                        # 格式化时间
                        if 'created_at' in code_df.columns:
                            code_df['created_at'] = pd.to_datetime(code_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        if 'used_at' in code_df.columns:
                            code_df['used_at'] = pd.to_datetime(code_df['used_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 选择要显示的列
                        display_columns = [
                            'code_prefix', 'amount', 'created_by', 'used_by', 
                            'used_in_group', 'created_at', 'used_at'
                        ]
                        
                        # 确保所有列都存在
                        display_columns = [col for col in display_columns if col in code_df.columns]
                        
                        # 显示已使用兑换码表格
                        st.dataframe(code_df[display_columns], use_container_width=True)
                        
                        # 显示统计信息
                        total_used = len(code_df)
                        total_amount = code_df['amount'].sum()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("已使用兑换码总数", total_used)
                        with col2:
                            st.metric("已兑换总金额", f"¥{total_amount:.2f}")
                        
                        # 按用户统计
                        if 'used_by' in code_df.columns:
                            user_stats = code_df.groupby('used_by').agg({
                                'amount': ['count', 'sum']
                            }).reset_index()
                            user_stats.columns = ['用户名', '使用次数', '累计金额']
                            st.write("\n**用户使用统计**")
                            st.dataframe(user_stats, use_container_width=True)
                        
                        # 按群组统计
                        if 'used_in_group' in code_df.columns:
                            group_stats = code_df.groupby('used_in_group').agg({
                                'amount': ['count', 'sum']
                            }).reset_index()
                            group_stats.columns = ['群组', '使用次数', '累计金额']
                            st.write("\n**群组使用统计**")
                            st.dataframe(group_stats, use_container_width=True)
                    else:
                        st.info("暂无已使用的兑换码")
                else:
                    st.error(f"获取统计失败: {response.text}")
            except Exception as e:
                st.error(f"获取出错: {str(e)}")
    
    # 交易管理
    elif selected_tab == "💰 交易管理":
        st.write("---")
        st.subheader("💰 交易管理功能正在开发中...")
        st.info("敬请期待更多功能的上线！")
    
    # 管理兑换码功能
    st.write("---")
    st.subheader("📋 兑换码管理")
    
    tab1, tab2 = st.tabs(["所有兑换码", "我生成的兑换码"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔄 查看所有兑换码"):
                try:
                    response = requests.get(f"{API}/codes")
                    if response.status_code == 200:
                        codes = response.json()
                        
                        if codes:
                            # 转换为DataFrame进行展示
                            code_df = pd.DataFrame(codes)
                            
                            # 格式化时间
                            if 'created_at' in code_df.columns:
                                code_df['created_at'] = pd.to_datetime(code_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                            if 'used_at' in code_df.columns:
                                code_df['used_at'] = pd.to_datetime(code_df['used_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                            # 添加状态显示
                            code_df['status'] = code_df['is_used'].apply(lambda x: '✅ 已使用' if x else '🔴 未使用')
                        
                            # 选择要显示的列
                            display_columns = [
                                'code_prefix', 'amount', 'status', 'created_by', 
                                'used_by', 'used_in_group', 'created_at', 'used_at'
                            ]
                        
                            # 确保所有列都存在
                            display_columns = [col for col in display_columns if col in code_df.columns]
                        
                            # 显示兑换码表格
                            st.dataframe(code_df[display_columns], use_container_width=True)
                            
                            # 显示统计信息
                            total_codes = len(code_df)
                            used_codes = code_df['is_used'].sum()
                            unused_codes = total_codes - used_codes
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("总兑换码数", total_codes)
                            with col2:
                                st.metric("已使用", used_codes)
                            with col3:
                                st.metric("未使用", unused_codes)
                            
                            # 导出未使用兑换码功能
                            st.write("---")
                            st.subheader("💾 导出未使用兑换码")
                            
                            # 过滤未使用的兑换码
                            unused_code_df = code_df[code_df['is_used'] == False]
                            
                            if len(unused_code_df) > 0:
                                # 准备导出数据
                                export_data = unused_code_df[['code_prefix', 'amount', 'created_at']]
                                export_data.columns = ['兑换码', '金额', '生成时间']
                                
                                # 将DataFrame转换为CSV
                                csv = export_data.to_csv(index=False, encoding='utf-8-sig')
                                
                                # 添加下载按钮
                                st.download_button(
                                    label="📥 导出未使用兑换码",
                                    data=csv,
                                    file_name="unused_codes.csv",
                                    mime="text/csv",
                                    help="导出所有未使用的兑换码及其对应金额"
                                )
                                
                                st.success(f"发现 {len(unused_code_df)} 个未使用的兑换码，可以导出。")
                            else:
                                st.info("暂无未使用的兑换码可供导出。")
                        else:
                            st.info("暂无兑换码")
                    else:
                        st.error(f"获取兑换码失败: {response.text}")
                except Exception as e:
                    st.error(f"获取出错: {str(e)}")
        
        with col2:
            st.subheader("💾 快速导出")
            if st.button("📥 一键导出未使用兑换码"):
                try:
                    response = requests.get(f"{API}/codes")
                    if response.status_code == 200:
                        codes = response.json()
                        
                        if codes:
                            # 转换为DataFrame
                            code_df = pd.DataFrame(codes)
                            
                            # 过滤未使用的兑换码
                            unused_code_df = code_df[code_df['is_used'] == False]
                            
                            if len(unused_code_df) > 0:
                                # 准备导出数据
                                export_data = unused_code_df[['code_prefix', 'amount', 'created_at']]
                                export_data.columns = ['兑换码', '金额', '生成时间']
                                
                                # 格式化时间
                                if '生成时间' in export_data.columns:
                                    export_data['生成时间'] = pd.to_datetime(export_data['生成时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
                                
                                # 将DataFrame转换为CSV
                                csv = export_data.to_csv(index=False, encoding='utf-8-sig')
                                
                                # 添加下载按钮
                                st.download_button(
                                    label="📥 下载CSV文件",
                                    data=csv,
                                    file_name="unused_codes.csv",
                                    mime="text/csv",
                                    help="导出所有未使用的兑换码及其对应金额"
                                )
                                
                                st.success(f"成功导出 {len(unused_code_df)} 个未使用的兑换码！")
                            else:
                                st.info("暂无未使用的兑换码可供导出。")
                        else:
                            st.info("暂无兑换码")
                    else:
                        st.error(f"获取兑换码失败: {response.text}")
                except Exception as e:
                    st.error(f"导出出错: {str(e)}")
            
            # 显示导出说明
            st.info("💡 点击按钮可以快速导出所有未使用的兑换码及其对应金额，方便进行管理和分发。")
    
    with tab2:
        if st.button("🔄 查看我生成的兑换码"):
            try:
                response = requests.get(f"{API}/users/{admin['id']}/codes")
                if response.status_code == 200:
                    codes = response.json()
                    
                    if codes:
                        # 转换为DataFrame进行展示
                        code_df = pd.DataFrame(codes)
                        
                        # 格式化时间
                        if 'created_at' in code_df.columns:
                            code_df['created_at'] = pd.to_datetime(code_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                        if 'used_at' in code_df.columns:
                            code_df['used_at'] = pd.to_datetime(code_df['used_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                        # 添加状态显示
                        code_df['status'] = code_df['is_used'].apply(lambda x: '✅ 已使用' if x else '🔴 未使用')
                    
                        # 选择要显示的列
                        display_columns = [
                            'code_prefix', 'amount', 'status', 
                            'used_by', 'used_in_group', 'created_at', 'used_at'
                        ]
                    
                        # 确保所有列都存在
                        display_columns = [col for col in display_columns if col in code_df.columns]
                    
                        # 显示兑换码表格
                        st.dataframe(code_df[display_columns], use_container_width=True)
                        
                        # 显示统计信息
                        total_codes = len(code_df)
                        used_codes = code_df['is_used'].sum()
                        unused_codes = total_codes - used_codes
                        total_amount = code_df['amount'].sum()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("总兑换码数", total_codes)
                        with col2:
                            st.metric("已使用", used_codes)
                        with col3:
                            st.metric("未使用", unused_codes)
                        with col4:
                            st.metric("总金额", f"¥{total_amount:.2f}")
                    else:
                        st.info("您还没有生成任何兑换码")
                else:
                    st.error(f"获取兑换码失败: {response.text}")
            except Exception as e:
                st.error(f"获取出错: {str(e)}")
    
    # 查看已使用的兑换码
    st.write("---")
    st.subheader("📊 兑换码使用统计")
    
    if st.button("🔄 查看使用统计"):
        try:
            response = requests.get(f"{API}/codes/used")
            if response.status_code == 200:
                used_codes = response.json()
                
                if used_codes:
                    # 转换为DataFrame进行展示
                    code_df = pd.DataFrame(used_codes)
                    
                    # 格式化时间
                    if 'created_at' in code_df.columns:
                        code_df['created_at'] = pd.to_datetime(code_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    if 'used_at' in code_df.columns:
                        code_df['used_at'] = pd.to_datetime(code_df['used_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 选择要显示的列
                    display_columns = [
                        'code_prefix', 'amount', 'created_by', 'used_by', 
                        'used_in_group', 'created_at', 'used_at'
                    ]
                    
                    # 确保所有列都存在
                    display_columns = [col for col in display_columns if col in code_df.columns]
                    
                    # 显示已使用兑换码表格
                    st.dataframe(code_df[display_columns], use_container_width=True)
                    
                    # 显示统计信息
                    total_used = len(code_df)
                    total_amount = code_df['amount'].sum()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("已使用兑换码总数", total_used)
                    with col2:
                        st.metric("已兑换总金额", f"¥{total_amount:.2f}")
                    
                    # 按用户统计
                    if 'used_by' in code_df.columns:
                        user_stats = code_df.groupby('used_by').agg({
                            'amount': ['count', 'sum']
                        }).reset_index()
                        user_stats.columns = ['用户名', '使用次数', '累计金额']
                        st.write("\n**用户使用统计**")
                        st.dataframe(user_stats, use_container_width=True)
                    
                    # 按群组统计
                    if 'used_in_group' in code_df.columns:
                        group_stats = code_df.groupby('used_in_group').agg({
                            'amount': ['count', 'sum']
                        }).reset_index()
                        group_stats.columns = ['群组', '使用次数', '累计金额']
                        st.write("\n**群组使用统计**")
                        st.dataframe(group_stats, use_container_width=True)
                else:
                    st.info("暂无已使用的兑换码")
            else:
                st.error(f"获取统计失败: {response.text}")
        except Exception as e:
            st.error(f"获取出错: {str(e)}")

# 主应用逻辑
if st.session_state.admin is None:
    admin_login()
else:
    admin_dashboard()