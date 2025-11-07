# 数据库增删改查与核心业务逻辑（分摊、结算）

from sqlmodel import Session, select
from .models import User, Group, Transaction, TransactionParticipant
from .schemas import CreateTransaction
from typing import List
from app import models

def create_user(session: Session, name: str, public_info: str = None):
    """创建新用户"""
    user = models.User(name=name, public_info=public_info)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int):
    """根据ID获取用户"""
    return session.get(models.User, user_id)


def get_all_users(session: Session):
    """列出所有用户"""
    return session.query(models.User).all()

def create_group(session: Session, name: str) -> Group:
    g = Group(name=name)
    session.add(g)
    session.commit()
    session.refresh(g)
    return g

def create_transaction(session: Session, payload: CreateTransaction):
    # 参与人数量
    n = len(payload.participants)

    # 创建交易记录
    transaction = Transaction(
        group_id=payload.group_id,
        payer_id=payload.payer_id,
        total_amount=payload.total_amount,
        description=payload.description
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    # 为每个参与者创建记录
    for p in payload.participants:
        participant = TransactionParticipant(
            transaction_id=transaction.id,
            user_id=p.user_id,
            share_amount=p.share_amount,
            paid_amount=p.paid_amount,
        )
        session.add(participant)

    session.commit()
    session.refresh(transaction)
    return transaction


def compute_user_balance(session: Session, user_id: int) -> float:
    # balance = sum(paid_amount) - sum(share_amount) across all txs
    paid_stmt = select(TransactionParticipant).where(TransactionParticipant.user_id == user_id)
    parts = session.exec(paid_stmt).all()
    paid = sum(p.paid_amount for p in parts)
    share = sum(p.share_amount for p in parts)
    return round(paid - share, 2)
