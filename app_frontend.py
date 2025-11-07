import streamlit as st
import requests

API = "http://127.0.0.1:8000"

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
    res = requests.get(f"{API}/users")
    if res.status_code == 200:
        users = res.json()
        st.table(users)
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
    res = requests.get(f"{API}/groups")
    if res.status_code == 200:
        st.table(res.json())

# ====================
# 交易管理
# ====================
st.header("💵 添加交易")

group_id = st.number_input("群组ID", step=1)
payer_id = st.number_input("付款人ID", step=1)
amount = st.number_input("总金额", step=1.0)
desc = st.text_input("交易说明")

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
            "participants": participants
        }
        res = requests.post(f"{API}/transactions", json=data)
        if res.status_code == 200:
            st.success(f"交易已添加: {res.json()}")
        else:
            st.error(res.text)
    except Exception as e:
        st.error(f"格式错误: {e}")

if st.button("📋 查看所有交易"):
    res = requests.get(f"{API}/transactions")
    if res.status_code == 200:
        st.table(res.json())

