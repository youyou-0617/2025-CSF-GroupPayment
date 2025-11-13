import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="用户端 - AA 群组记账", page_icon="👤", layout="centered")

# 初始化会话状态
if 'user' not in st.session_state:
    st.session_state.user = None

# 主应用
if st.session_state.user is None:
    # 登录页面
    st.title("👤 用户登录")
    st.write("请输入您的用户名进行登录")
    
    with st.form("login_form"):
        username = st.text_input("用户名")
        submit = st.form_submit_button("登录")
    
    if submit:
        if not username.strip():
            st.error("请输入用户名")
        else:
            try:
                # 调用登录API
                response = requests.post(f"{API}/users/login", params={"user_name": username})
                if response.status_code == 200:
                    user_data = response.json()
                    st.session_state.user = user_data
                    st.success(f"登录成功！欢迎回来，{username}")
                    # 刷新页面显示登录后的内容
                    st.rerun()
                else:
                    st.error(f"登录失败: {response.text}")
            except Exception as e:
                st.error(f"登录出错: {str(e)}")
else:
    # 登录后的主页面
    user = st.session_state.user
    st.title(f"👤 欢迎回来，{user['name']}")
    
    # 登出按钮
    if st.button("退出登录"):
        st.session_state.user = None
        st.rerun()
    
    # 查看用户所在群组和余额
    st.write("---")
    st.subheader("📊 我的群组和余额")
    
    if st.button("🔄 刷新群组信息"):
        try:
            response = requests.get(f"{API}/users/{user['id']}/groups")
            if response.status_code == 200:
                data = response.json()
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
    
    # 查看特定群组的详细信息
    st.write("---")
    st.subheader("👥 群组详情")
    
    group_id_input = st.number_input("输入群组ID查看详情", step=1)
    if st.button("👁️ 查看群组详情"):
        try:
            response = requests.get(f"{API}/groups/{group_id_input}")
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
            else:
                st.error(f"获取群组详情失败: {response.text}")
        except Exception as e:
            st.error(f"获取群组详情出错: {str(e)}")
    
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