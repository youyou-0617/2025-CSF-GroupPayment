# 数据库增删改查与核心业务逻辑（分摊、结算）

from sqlmodel import Session, select
from .models import User, Group, Transaction, TransactionParticipant, GroupMember
from .schemas import CreateTransaction
from typing import List, Optional
import random
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

def get_user_by_name(session: Session, name: str) -> Optional[models.User]:
    """根据用户名获取用户
    
    Args:
        session: 数据库会话
        name: 用户名
    
    Returns:
        Optional[models.User]: 用户对象，如果不存在返回None
    """
    stmt = select(models.User).where(models.User.name == name)
    return session.exec(stmt).first()


def get_all_users(session: Session):
    """列出所有用户"""
    return session.query(models.User).all()

def delete_user(session: Session, user_id: int) -> bool:
    """删除用户
    
    Args:
        session: 数据库会话
        user_id: 用户ID
    
    Returns:
        bool: 是否删除成功
    
    Raises:
        ValueError: 当用户不存在时
    """
    # 获取用户
    user = get_user(session, user_id)
    if not user:
        raise ValueError("用户不存在")
    
    # 删除用户在所有群组中的成员关系
    stmt = select(models.GroupMember).where(models.GroupMember.user_id == user_id)
    member_relations = session.exec(stmt).all()
    for relation in member_relations:
        session.delete(relation)
    
    # 删除用户参与的交易记录
    stmt = select(models.TransactionParticipant).where(models.TransactionParticipant.user_id == user_id)
    participant_relations = session.exec(stmt).all()
    for relation in participant_relations:
        session.delete(relation)
    
    # 删除用户
    session.delete(user)
    session.commit()
    return True

def create_group(session: Session, name: str) -> Group:
    """创建群组"""
    g = Group(name=name)
    session.add(g)
    session.commit()
    session.refresh(g)
    return g

def get_group(session: Session, group_id: int) -> Optional[Group]:
    """获取群组信息"""
    return session.get(models.Group, group_id)

def get_all_groups(session: Session):
    """获取所有群组"""
    return session.query(models.Group).all()

def delete_group(session: Session, group_id: int) -> bool:
    """删除群组
    
    Args:
        session: 数据库会话
        group_id: 群组ID
    
    Returns:
        bool: 是否删除成功
    
    Raises:
        ValueError: 当群组不存在时
    """
    # 获取群组
    group = get_group(session, group_id)
    if not group:
        raise ValueError("群组不存在")
    
    # 删除群组成员关系
    stmt = select(models.GroupMember).where(models.GroupMember.group_id == group_id)
    members = session.exec(stmt).all()
    for member in members:
        session.delete(member)
    
    # 删除群组
    session.delete(group)
    session.commit()
    return True

def add_user_to_group(session: Session, user_id: int, group_id: int, initial_balance: float = 0.0) -> GroupMember:
    """添加用户到群组并设置初始余额"""
    # 检查用户和群组是否存在
    user = get_user(session, user_id)
    group = get_group(session, group_id)
    if not user or not group:
        raise ValueError("用户或群组不存在")
    
    # 检查用户是否已经在群组中
    stmt = select(GroupMember).where(
        GroupMember.user_id == user_id,
        GroupMember.group_id == group_id
    )
    existing = session.exec(stmt).first()
    if existing:
        raise ValueError("用户已经在该群组中")
    
    # 创建群组成员记录
    member = GroupMember(
        user_id=user_id,
        group_id=group_id,
        balance=initial_balance
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return member

def update_group_member_balance(session: Session, user_id: int, group_id: int, balance_change: float) -> GroupMember:
    """更新用户在群组中的余额"""
    stmt = select(GroupMember).where(
        GroupMember.user_id == user_id,
        GroupMember.group_id == group_id
    )
    member = session.exec(stmt).first()
    if not member:
        raise ValueError("用户不在该群组中")
    
    # 更新余额并确保精度
    member.balance = round(member.balance + balance_change, 2)
    session.commit()
    session.refresh(member)
    return member

def get_group_members(session: Session, group_id: int) -> List[GroupMember]:
    """获取群组所有成员"""
    stmt = select(GroupMember).where(GroupMember.group_id == group_id)
    return session.exec(stmt).all()

def get_user_groups(session: Session, user_id: int) -> List[dict]:
    """获取用户所在的所有群组及其在群组中的余额
    
    Args:
        session: 数据库会话
        user_id: 用户ID
    
    Returns:
        List[dict]: 包含群组信息和用户在该群组余额的列表
    """
    # 查询用户的群组成员关系
    stmt = select(GroupMember).where(GroupMember.user_id == user_id)
    member_relations = session.exec(stmt).all()
    
    groups_info = []
    for relation in member_relations:
        # 获取群组信息
        group = get_group(session, relation.group_id)
        if group:
            groups_info.append({
                "group_id": group.id,
                "group_name": group.name,
                "balance": relation.balance,
                "joined_at": relation.joined_at
            })
    
    return groups_info

def calculate_aa_amounts(total_amount: float, participant_count: int) -> List[float]:
    """计算AA分摊金额，处理除不尽的情况"""
    # 计算基础金额（保留两位小数）
    base_amount = round(total_amount / participant_count, 2)
    
    # 计算总金额
    total_calculated = base_amount * participant_count
    
    # 计算差值
    difference = round(total_amount - total_calculated, 2)
    
    # 生成金额列表
    amounts = [base_amount] * participant_count
    
    # 处理差值，随机选择用户增加0.01
    if difference > 0:
        # 需要增加的人数
        add_count = int(difference * 100)
        # 随机选择add_count个用户
        indices_to_add = random.sample(range(participant_count), add_count)
        for idx in indices_to_add:
            amounts[idx] = round(amounts[idx] + 0.01, 2)
    
    return amounts

def create_transaction(session: Session, payload: CreateTransaction):
    """创建交易（AA模式）"""
    # 检查付款人是否在参与者列表中
    if payload.payer_id not in payload.participants:
        raise ValueError("付款人必须是参与者之一")
    
    # 获取参与者数量
    participant_count = len(payload.participants)
    
    # 计算AA分摊金额
    share_amounts = calculate_aa_amounts(payload.total_amount, participant_count)
    
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
    
    # 为每个参与者创建记录并更新群组余额
    for i, user_id in enumerate(payload.participants):
        share_amount = share_amounts[i]
        paid_amount = payload.total_amount if user_id == payload.payer_id else 0.0
        
        # 创建交易参与者记录
        participant = TransactionParticipant(
            transaction_id=transaction.id,
            user_id=user_id,
            share_amount=share_amount,
            paid_amount=paid_amount,
            settled=True  # 简化处理，自动结算
        )
        session.add(participant)
        
        # 更新群组成员余额
        # 所有人（包括付款人）都应该扣除自己的份额
        # 付款人只是名义上的负责人，不是实际获得款项的人
        balance_change = -share_amount
        try:
            update_group_member_balance(session, user_id, payload.group_id, balance_change)
        except ValueError:
            # 如果用户不在群组中，可以选择忽略或抛出错误
            # 这里选择继续执行，让业务层决定如何处理
            pass
    
    session.commit()
    session.refresh(transaction)
    return transaction

def get_transaction(session: Session, transaction_id: int) -> Optional[Transaction]:
    """获取交易详情"""
    return session.get(models.Transaction, transaction_id)

def get_all_transactions(session: Session) -> List[Transaction]:
    """获取所有交易"""
    return session.query(models.Transaction).all()

def get_transaction_participants(session: Session, transaction_id: int) -> List[TransactionParticipant]:
    """获取交易的所有参与者"""
    stmt = select(TransactionParticipant).where(TransactionParticipant.transaction_id == transaction_id)
    return session.exec(stmt).all()

def get_user_transactions(session: Session, user_id: int) -> List[dict]:
    """获取用户参与的所有交易记录
    
    Args:
        session: 数据库会话
        user_id: 用户ID
    
    Returns:
        List[dict]: 包含交易信息的列表
    """
    # 查询用户参与的交易记录
    stmt = select(TransactionParticipant).where(TransactionParticipant.user_id == user_id)
    participant_relations = session.exec(stmt).all()
    
    transactions = []
    for relation in participant_relations:
        # 获取交易信息
        transaction = get_transaction(session, relation.transaction_id)
        if transaction:
            # 获取群组信息
            group = get_group(session, transaction.group_id)
            # 获取付款人信息
            payer = get_user(session, transaction.payer_id)
            
            # 判断当前用户是否为付款人
            is_payer = user_id == transaction.payer_id
            
            transaction_info = {
                "transaction_id": transaction.id,
                "group_id": transaction.group_id,
                "group_name": group.name if group else "未知群组",
                "description": transaction.description,
                "total_amount": transaction.total_amount,
                "is_payer": is_payer,
                "payer_name": payer.name if payer else "未知用户",
                "my_share": relation.share_amount,
                "my_paid": relation.paid_amount,
                "created_at": transaction.created_at
            }
            transactions.append(transaction_info)
    
    # 按创建时间倒序排列
    transactions.sort(key=lambda x: x['created_at'], reverse=True)
    return transactions

def compute_user_balance(session: Session, user_id: int) -> float:
    """计算用户在所有交易中的总余额"""
    # balance = sum(paid_amount) - sum(share_amount) across all txs
    paid_stmt = select(TransactionParticipant).where(TransactionParticipant.user_id == user_id)
    parts = session.exec(paid_stmt).all()
    paid = sum(p.paid_amount for p in parts)
    share = sum(p.share_amount for p in parts)
    return round(paid - share, 2)
