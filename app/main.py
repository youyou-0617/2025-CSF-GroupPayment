from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from .db import init_db, get_session
from . import crud, schemas
from app.models import User, Group, Transaction, TransactionParticipant

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
@app.post("/users")
def create_user(u: schemas.CreateUser, session: Session = Depends(get_session)):
    user = crud.create_user(session, u.name, u.public_info)
    return user

@app.get("/users")
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/balance")
def user_balance(user_id: int, session: Session = Depends(get_session)):
    bal = crud.compute_user_balance(session, user_id)
    return {"user_id": user_id, "balance": bal}

# ------------------------
# 群组 CRUD
# ------------------------
@app.post("/groups")
def create_group(g: schemas.CreateGroup, session: Session = Depends(get_session)):
    group = crud.create_group(session, g.name)
    return {"id": group.id, "name": group.name}

@app.get("/groups")
def list_groups(session: Session = Depends(get_session)):
    groups = session.exec(select(Group)).all()
    return groups

@app.get("/groups/{group_id}")
def get_group(group_id: int, session: Session = Depends(get_session)):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# ------------------------
# 交易 CRUD
# ------------------------
@app.post("/transactions")
def create_transaction(payload: schemas.CreateTransaction, session: Session = Depends(get_session)):
    if payload.payer_id not in [p.user_id for p in payload.participants]:
        raise HTTPException(status_code=400, detail="payer must be in participant_ids")
    tx = crud.create_transaction(session, payload)
    return {"transaction_id": tx.id, "total": tx.total_amount}

@app.get("/transactions")
def list_transactions(session: Session = Depends(get_session)):
    txs = session.exec(select(Transaction)).all()
    return txs

@app.get("/transactions/{tx_id}")
def get_transaction(tx_id: int, session: Session = Depends(get_session)):
    tx = session.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    participants = session.exec(
        select(TransactionParticipant).where(TransactionParticipant.transaction_id == tx_id)
    ).all()
    return {
        "transaction": tx,
        "participants": participants
    }

# ------------------------
# 参与人查看
# ------------------------
@app.get("/participants")
def list_participants(session: Session = Depends(get_session)):
    participants = session.exec(select(TransactionParticipant)).all()
    return participants
