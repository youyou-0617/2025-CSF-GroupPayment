from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from .db import init_db, get_session
from . import crud, schemas
from app.models import User, Group, Transaction, TransactionParticipant, GroupMember

app = FastAPI(title="Group Payment System")

# ------------------------
# 启动时初始化数据库
# ------------------------
@app.on_event("startup")
def on_startup():
    init_db()

# ------------------------
# 用户 CRUD
# ------------------------
@app.post("/users", response_model=schemas.UserOut)
def create_user(u: schemas.CreateUser, session: Session = Depends(get_session)):
    user = crud.create_user(session, u.name, u.public_info)
    return user

@app.get("/users", response_model=list[schemas.UserOut])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/balance")
def user_balance(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    balance = crud.compute_user_balance(session, user_id)
    return {"user_id": user_id, "user_name": user.name, "balance": balance}

@app.post("/users/login")
def user_login(user_name: str, session: Session = Depends(get_session)):
    """用户登录（根据用户名）"""
    user = crud.get_user_by_name(session, user_name)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "name": user.name,
        "public_info": user.public_info,
        "message": "登录成功"
    }

@app.get("/users/{user_id}/groups")
def get_user_groups(user_id: int, session: Session = Depends(get_session)):
    """获取用户所在的群组及其余额"""
    # 检查用户是否存在
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户所在的群组信息
    groups = crud.get_user_groups(session, user_id)
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "groups": groups
    }

@app.get("/users/{user_id}/transactions")
def get_user_transactions(user_id: int, session: Session = Depends(get_session)):
    """获取用户参与的所有交易记录"""
    # 检查用户是否存在
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户的交易记录
    transactions = crud.get_user_transactions(session, user_id)
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "transactions": transactions
    }

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """删除用户"""
    try:
        crud.delete_user(session, user_id)
        return {"message": "用户删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户时出错: {str(e)}")

# ------------------------
# 群组 CRUD
# ------------------------
@app.post("/groups", response_model=schemas.GroupOut)
def create_group(g: schemas.CreateGroup, session: Session = Depends(get_session)):
    # 创建群组
    group = crud.create_group(session, g.name)
    
    # 添加成员到群组
    added_count = 0
    failed_count = 0
    
    if g.member_ids:
        for user_id in g.member_ids:
            try:
                crud.add_user_to_group(session, user_id, group.id)
                added_count += 1
            except ValueError as e:
                # 记录失败的添加
                failed_count += 1
                print(f"Failed to add user {user_id} to group {group.id}: {str(e)}")
                continue
    
    # 提交会话确保数据保存
    session.commit()
    session.refresh(group)
    
    # 返回带有添加状态信息的响应
    response = {
        "id": group.id,
        "name": group.name,
        "added_members": added_count,
        "failed_members": failed_count
    }
    
    return response

@app.get("/groups", response_model=list[schemas.GroupOut])
def list_groups(session: Session = Depends(get_session)):
    groups = crud.get_all_groups(session)
    return groups

@app.get("/groups/{group_id}", response_model=schemas.GroupOut)
def get_group(group_id: int, session: Session = Depends(get_session)):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # 获取群组成员信息
    members = crud.get_group_members(session, group_id)
    
    # 构建响应对象
    group_dict = {"id": group.id, "name": group.name, "members": []}
    for member in members:
        user = crud.get_user(session, member.user_id)
        member_dict = {
            "id": member.id,
            "user_id": member.user_id,
            "group_id": member.group_id,
            "balance": member.balance,
            "joined_at": member.joined_at,
            "user": user
        }
        group_dict["members"].append(member_dict)
    
    return group_dict

@app.delete("/groups/{group_id}")
def delete_group(group_id: int, session: Session = Depends(get_session)):
    """删除群组"""
    try:
        crud.delete_group(session, group_id)
        return {"message": "群组删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除群组时出错: {str(e)}")

# ------------------------
# 群组成员管理
# ------------------------
@app.post("/groups/{group_id}/members")
def add_user_to_group(group_id: int, user_data: schemas.AddUserToGroup, session: Session = Depends(get_session)):
    try:
        member = crud.add_user_to_group(session, user_data.user_id, group_id, user_data.initial_balance)
        return {"message": "User added to group successfully", "member_id": member.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/groups/{group_id}/members")
def list_group_members(group_id: int, session: Session = Depends(get_session)):
    # 检查群组是否存在
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    members = crud.get_group_members(session, group_id)
    result = []
    for member in members:
        user = crud.get_user(session, member.user_id)
        result.append({
            "id": member.id,
            "user": user,
            "balance": member.balance,
            "joined_at": member.joined_at
        })
    return result

@app.post("/groups/{group_id}/balance")
def update_group_balance(group_id: int, balance_data: schemas.UpdateGroupBalance, session: Session = Depends(get_session)):
    try:
        member = crud.update_group_member_balance(session, balance_data.user_id, group_id, balance_data.balance_change)
        return {"message": "Balance updated successfully", "new_balance": member.balance}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------
# 交易 CRUD
# ------------------------
@app.post("/transactions")
def create_transaction(payload: schemas.CreateTransaction, session: Session = Depends(get_session)):
    try:
        tx = crud.create_transaction(session, payload)
        return {"transaction_id": tx.id, "total": tx.total_amount, "message": "Transaction created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(session: Session = Depends(get_session)):
    txs = crud.get_all_transactions(session)
    result = []
    for tx in txs:
        participants = crud.get_transaction_participants(session, tx.id)
        tx_dict = {
            "id": tx.id,
            "group_id": tx.group_id,
            "payer_id": tx.payer_id,
            "total_amount": tx.total_amount,
            "description": tx.description,
            "created_at": tx.created_at,
            "participants": []
        }
        for p in participants:
            user = crud.get_user(session, p.user_id)
            p_dict = {
                "id": p.id,
                "user_id": p.user_id,
                "share_amount": p.share_amount,
                "paid_amount": p.paid_amount,
                "settled": p.settled,
                "user": user
            }
            tx_dict["participants"].append(p_dict)
        result.append(tx_dict)
    return result

@app.get("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, session: Session = Depends(get_session)):
    tx = crud.get_transaction(session, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    participants = crud.get_transaction_participants(session, tx_id)
    
    # 构建响应对象
    tx_dict = {
        "id": tx.id,
        "group_id": tx.group_id,
        "payer_id": tx.payer_id,
        "total_amount": tx.total_amount,
        "description": tx.description,
        "created_at": tx.created_at,
        "participants": []
    }
    
    for p in participants:
        user = crud.get_user(session, p.user_id)
        p_dict = {
            "id": p.id,
            "user_id": p.user_id,
            "share_amount": p.share_amount,
            "paid_amount": p.paid_amount,
            "settled": p.settled,
            "user": user
        }
        tx_dict["participants"].append(p_dict)
    
    return tx_dict

# ------------------------
# 参与人查看
# ------------------------
@app.get("/participants")
def list_participants(session: Session = Depends(get_session)):
    participants = session.exec(select(TransactionParticipant)).all()
    return participants
