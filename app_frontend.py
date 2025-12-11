import streamlit as st
import requests
import random
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

st.set_page_config(page_title="AA 群组记账", page_icon="💰", layout="centered")
st.title("💰 AA 群组记账 App")

# ====================
# 用户管理
# ====================
st.header("👤 用户管理")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("用户名")
with col2:
    info = st.text_input("公开信息")

if st.button("➕ 创建用户"):
    res = requests.post(f"{API}/users", json={"name": name, "public_info": info})
    if res.status_code == 200:
        st.success(f"创建成功: {res.json()}")
    else:
        st.error(res.text)

if st.button("📋 查看所有用户"):
    import pandas as pd
    res = requests.get(f"{API}/users")
    if res.status_code == 200:
        users = res.json()
        if users:
            # 创建一个DataFrame来展示用户列表
            user_data = [[user["id"], user["name"], user["public_info"]] for user in users]
            df = pd.DataFrame(user_data, columns=["ID", "姓名", "公开信息"])
            st.dataframe(df)
            
            # 删除用户功能
            st.subheader("删除用户")
            user_to_delete = st.selectbox(
                "选择要删除的用户",
                [f"{user['name']} (ID: {user['id']})" for user in users],
                index=None,
                placeholder="请选择用户"
            )
            
            if user_to_delete:
                # 提取用户ID
                user_id = int(user_to_delete.split("ID: ")[-1].strip(")"))
                if st.button(f"删除用户 {user_to_delete.split(' (ID:')[0]}", type="primary", help="删除用户将同时删除其所有群组成员关系和交易记录"):
                    try:
                        delete_response = requests.delete(f"{API}/users/{user_id}")
                        if delete_response.status_code == 200:
                            st.success("用户删除成功")
                            # 刷新页面
                            st.rerun()
                        else:
                            st.error(f"删除用户失败: {delete_response.text}")
                    except Exception as e:
                        st.error(f"删除用户出错: {str(e)}")
        else:
            st.info("暂无用户数据")
    else:
        st.error("无法获取用户列表")

# ====================
# 群组管理
# ====================
st.header("👥 群组管理")

group_name = st.text_input("群组名")
member_ids = st.text_input("成员ID（用逗号分隔）")

if st.button("➕ 创建群组"):
    try:
        members = [int(x.strip()) for x in member_ids.split(",") if x.strip()]
        res = requests.post(f"{API}/groups", json={"name": group_name, "member_ids": members})
        if res.status_code == 200:
            st.success(f"群组创建成功: {res.json()}")
        else:
            st.error(res.text)
    except Exception as e:
        st.error(f"输入错误: {e}")

if st.button("📋 查看所有群组"):
    import pandas as pd
    res = requests.get(f"{API}/groups")
    if res.status_code == 200:
        groups = res.json()
        if groups:
            # 创建DataFrame展示群组列表
            group_data = [[group["id"], group["name"], len(group.get("members", []))] for group in groups]
            df = pd.DataFrame(group_data, columns=["ID", "群组名称", "成员数量"])
            st.dataframe(df)
            
            # 删除群组功能
            st.subheader("删除群组")
            group_to_delete = st.selectbox(
                "选择要删除的群组",
                [f"{group['name']} (ID: {group['id']})" for group in groups],
                index=None,
                placeholder="请选择群组"
            )
            
            if group_to_delete:
                # 提取群组ID
                group_id = int(group_to_delete.split("ID: ")[-1].strip(")"))
                if st.button(f"删除群组 {group_to_delete.split(' (ID:')[0]}", type="primary", help="删除群组将同时删除其所有群组成员关系"):
                    try:
                        delete_response = requests.delete(f"{API}/groups/{group_id}")
                        if delete_response.status_code == 200:
                            st.success("群组删除成功")
                            # 刷新页面
                            st.rerun()
                        else:
                            st.error(f"删除群组失败: {delete_response.text}")
                    except Exception as e:
                        st.error(f"删除群组出错: {str(e)}")
        else:
            st.info("暂无群组数据")
    else:
        st.error("无法获取群组列表")

# 查看群组详情和成员
st.subheader("📊 群组详情")
group_id_view = st.number_input("输入群组ID查看详情", step=1)
if st.button("👁️ 查看群组详情"):
    res = requests.get(f"{API}/groups/{group_id_view}")
    if res.status_code == 200:
        group = res.json()
        st.write("**群组信息**")
        st.write(f"群组名称: {group['name']}")
        st.write("\n**成员列表及余额**")
        if 'members' in group and group['members']:
            st.table([{
                "用户ID": member['user_id'],
                "用户名": member.get('user', {}).get('name', '未知用户') if 'user' in member else '未知用户',
                "余额": member['balance']
            } for member in group['members']])
        else:
            st.write("该群组暂无成员")
    else:
        st.error("无法获取群组信息")

# 添加成员到群组
st.subheader("👤 添加成员")
group_id_add_member = st.number_input("群组ID", step=1, key="group_add")
user_id_add = st.number_input("用户ID", step=1, key="user_add")
initial_balance = st.number_input("初始余额（默认为0）", step=0.01, value=0.0, key="balance_add")

if st.button("➕ 添加成员到群组"):
    res = requests.post(f"{API}/groups/{group_id_add_member}/members", 
                      json={"user_id": user_id_add, "initial_balance": initial_balance, "group_id": group_id_add_member})
    if res.status_code == 200:
        st.success(f"成员添加成功: {res.json()}")
    else:
        st.error(res.text)

# 更新成员余额
st.subheader("💵 更新余额")
group_id_balance = st.number_input("群组ID", step=1, key="group_balance")
user_id_balance = st.number_input("用户ID", step=1, key="user_balance")
balance_change = st.number_input("余额变更（正数增加，负数减少）", step=0.01, key="balance_change")

if st.button("📈 更新余额"):
    res = requests.post(f"{API}/groups/{group_id_balance}/balance", 
                      json={"user_id": user_id_balance, "balance_change": balance_change, "group_id": group_id_balance})
    if res.status_code == 200:
        st.success(f"余额更新成功: {res.json()}")
    else:
        st.error(res.text)

# ====================
# 交易管理
# ====================
st.header("💵 添加交易")

# 交易类型选择
transaction_type = st.radio("交易类型", ["自定义分摊", "AA制扣款"])

group_id = st.number_input("群组ID", step=1)
payer_id = st.number_input("付款人ID", step=1)
amount = st.number_input("总金额", step=0.01)
desc = st.text_input("交易说明")

if transaction_type == "自定义分摊":
    st.write("参与者（格式: 用户ID, 应分金额, 实付金额）")
    participants_str = st.text_area("示例: 1,50,50\n2,50,0")
    
    if st.button("➕ 添加交易"):
        try:
            participants = []
            for line in participants_str.splitlines():
                if not line.strip():
                    continue
                user_id, share, paid = [x.strip() for x in line.split(",")]
                participants.append({
                    "user_id": int(user_id),
                    "share_amount": float(share),
                    "paid_amount": float(paid)
                })
            data = {
                "group_id": group_id,
                "payer_id": payer_id,
                "total_amount": amount,
                "description": desc,
                "participants": participants,
                "is_aa": False
            }
            res = requests.post(f"{API}/transactions", json=data)
            if res.status_code == 200:
                st.success(f"交易已添加: {res.json()}")
            else:
                st.error(res.text)
        except Exception as e:
            st.error(f"格式错误: {e}")
else:  # AA制扣款
    st.write("参与者（格式: 用户ID，多个ID用逗号分隔）")
    participant_ids_str = st.text_input("示例: 1,2,3")
    
    if st.button("➕ 添加AA交易"):
        try:
            participant_ids = [int(x.strip()) for x in participant_ids_str.split(",") if x.strip()]
            data = {
                "group_id": group_id,
                "payer_id": payer_id,
                "total_amount": amount,
                "description": desc,
                "participants": participant_ids,
                "is_aa": True
            }
            res = requests.post(f"{API}/transactions", json=data)
            if res.status_code == 200:
                transaction = res.json()
                st.success(f"AA交易已添加")
                st.write("**分摊详情**")
                if 'participants' in transaction:
                    st.table([{
                        "用户ID": p['user_id'],
                        "分摊金额": p['share_amount']
                    } for p in transaction['participants']])
            else:
                st.error(res.text)
        except Exception as e:
            st.error(f"格式错误: {e}")

if st.button("📋 查看所有交易"):
    res = requests.get(f"{API}/transactions")
    if res.status_code == 200:
        st.table(res.json())
    else:
        st.error("无法获取交易列表")

# 查看群组交易
st.subheader("📊 群组交易记录")
group_id_transactions = st.number_input("输入群组ID查看交易", step=1)
if st.button("📈 查看群组交易"):
    res = requests.get(f"{API}/transactions/group/{group_id_transactions}")
    if res.status_code == 200:
        transactions = res.json()
        st.table(transactions)
    else:
        st.error("无法获取群组交易记录")

