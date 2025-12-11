# 数据库增删改查与核心业务逻辑（分摊、结算）

from sqlmodel import Session, select
from .models import User, Group, Transaction, TransactionParticipant, GroupMember, Code
from .schemas import CreateTransaction
from typing import List, Optional
import random
import string
import bcrypt
from datetime import datetime, timedelta
from app import models

def hash_password(password: str) -> str:
    """使用bcrypt安全哈希密码
    
    Args:
        password: 原始密码
    
    Returns:
        str: 哈希后的密码（包含盐值）
    """
    # 生成随机盐值并使用bcrypt算法哈希密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 原始密码
        hashed_password: 哈希后的密码
    
    Returns:
        bool: 密码是否匹配
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_user(session: Session, name: str, public_info: str = None, password: str = None):
    """创建新用户"""
    hashed_password = None
    if password:
        hashed_password = hash_password(password)
    user = models.User(name=name, public_info=public_info, password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_name_and_password(session: Session, name: str, password: str) -> Optional[models.User]:
    """根据用户名和密码获取用户（用于登录验证）
    
    Args:
        session: 数据库会话
        name: 用户名
        password: 密码
    
    Returns:
        Optional[models.User]: 用户对象，如果不存在或密码错误返回None
    """
    stmt = select(models.User).where(models.User.name == name)
    user = session.exec(stmt).first()
    
    if user and user.password and verify_password(password, user.password):
        return user
    
    return None


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
    """获取所有群组及其成员信息"""
    groups = session.query(models.Group).all()
    result = []
    
    for group in groups:
        # 获取群组成员信息
        members = get_group_members(session, group.id)
        # 构建包含成员信息的群组字典
        group_dict = {
            "id": group.id,
            "name": group.name,
            "members": [
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "group_id": member.group_id,
                    "balance": member.balance,
                    "joined_at": member.joined_at,
                    "user": get_user(session, member.user_id)
                }
                for member in members
            ]
        }
        result.append(group_dict)
    
    return result

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

# ------------------------
# 兑换码相关函数
# ------------------------

def generate_code(length: int = 12) -> str:
    """生成强随机兑换码
    
    Args:
        length: 兑换码长度，默认为12位（增加安全性）
    
    Returns:
        str: 生成的随机兑换码
    """
    # 使用大小写字母、数字和特殊字符生成更安全的随机码
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def hash_code(code: str, salt: str = None) -> tuple:
    """对兑换码进行哈希处理
    
    Args:
        code: 原始兑换码字符串
        salt: 盐值，如果不提供则自动生成
    
    Returns:
        tuple: (哈希后的兑换码, 使用的盐值)
    """
    if not salt:
        # 直接使用bcrypt.gensalt()生成盐值，然后解码存储
        bcrypt_salt = bcrypt.gensalt()
        salt = bcrypt_salt.decode('utf-8')
        hashed = bcrypt.hashpw(code.encode('utf-8'), bcrypt_salt)
    else:
        # 如果提供了盐值，使用它来计算哈希
        hashed = bcrypt.hashpw(code.encode('utf-8'), salt.encode('utf-8'))
    return hashed.decode('utf-8'), salt

def verify_code(code: str, hashed_code: str, salt: str) -> bool:
    """验证兑换码是否正确
    
    Args:
        code: 用户提供的原始兑换码
        hashed_code: 存储的哈希值
        salt: 存储的盐值（这里仍然保留参数以保持API兼容性，但在函数内部不使用）
    
    Returns:
        bool: 如果兑换码正确返回True，否则返回False
    """
    # 直接使用bcrypt.checkpw进行验证，这是bcrypt的正确验证方式
    # bcrypt的哈希值本身就包含了盐值信息
    return bcrypt.checkpw(code.encode('utf-8'), hashed_code.encode('utf-8'))

def create_code(session: Session, amount: float, created_by: int) -> dict:
    """创建新的兑换码
    
    Args:
        session: 数据库会话
        amount: 兑换码对应的金额
        created_by: 创建兑换码的用户ID
    
    Returns:
        dict: 包含原始兑换码和创建结果的字典
    """
    # 生成唯一的兑换码
    code_str = generate_code()
    
    # 对兑换码进行哈希处理
    code_hash, code_salt = hash_code(code_str)
    
    # 获取兑换码前缀用于显示（前6位）
    code_prefix = code_str[:6]
    
    # 检查相同前缀的兑换码是否已存在（降低冲突概率）
    while session.exec(select(Code).where(Code.code_prefix == code_prefix)).first():
        # 如果前缀已存在，重新生成兑换码
        code_str = generate_code()
        code_hash, code_salt = hash_code(code_str)
        code_prefix = code_str[:6]
    
    # 创建兑换码
    code = Code(
        code_hash=code_hash,
        code_salt=code_salt,
        code_prefix=code_prefix,
        amount=amount,
        created_by=created_by,
        expires_at=datetime.utcnow() + timedelta(days=30)  # 添加30天有效期
    )
    
    session.add(code)
    session.commit()
    session.refresh(code)
    
    # 返回原始兑换码和兑换码对象信息
    return {
        "id": code.id,
        "code": code_str,  # 返回原始兑换码（仅在创建时返回一次）
        "code_prefix": code_prefix,
        "amount": code.amount,
        "is_used": code.is_used,
        "created_by": code.created_by,
        "created_at": code.created_at,
        "expires_at": code.expires_at
    }

def get_code(session: Session, code_str: str) -> Optional[Code]:
    """根据兑换码字符串获取兑换码信息
    
    Args:
        session: 数据库会话
        code_str: 用户提供的兑换码字符串
    
    Returns:
        Optional[Code]: 兑换码对象，如果不存在返回None
    """
    # 由于我们不知道具体的盐值，需要先获取所有未使用的兑换码，然后逐一验证
    # 为了提高效率，我们可以先通过前缀过滤
    code_prefix = code_str[:6]
    
    # 获取具有相同前缀的未使用兑换码
    stmt = select(Code).where(
        Code.code_prefix == code_prefix,
        Code.is_used == False
    )
    
    potential_codes = session.exec(stmt).all()
    
    # 验证每个潜在的兑换码
    for code in potential_codes:
        if verify_code(code_str, code.code_hash, code.code_salt):
            return code
    
    # 如果没有找到匹配的兑换码，再检查是否有已使用的（用于错误提示）
    stmt = select(Code).where(Code.code_prefix == code_prefix)
    all_potential_codes = session.exec(stmt).all()
    
    for code in all_potential_codes:
        if verify_code(code_str, code.code_hash, code.code_salt):
            return code
    
    return None

def use_code(session: Session, code_str: str, user_id: int, group_id: int) -> dict:
    """使用兑换码，增加用户在群组中的余额
    
    Args:
        session: 数据库会话
        code_str: 兑换码字符串
        user_id: 使用兑换码的用户ID
        group_id: 使用兑换码的群组ID
    
    Returns:
        dict: 包含操作结果的字典
    
    Raises:
        ValueError: 当兑换码不存在、已使用、已过期、用户不在群组中或其他错误时
    """
    # 获取兑换码
    code = get_code(session, code_str)
    if not code:
        raise ValueError("兑换码不存在")
    
    # 检查兑换码是否已使用
    if code.is_used:
        raise ValueError("兑换码已被使用")
    
    # 检查兑换码是否已过期
    if hasattr(code, 'expires_at') and code.expires_at and code.expires_at < datetime.utcnow():
        raise ValueError("兑换码已过期")
    
    # 检查用户是否在群组中
    stmt = select(GroupMember).where(
        GroupMember.user_id == user_id,
        GroupMember.group_id == group_id
    )
    member = session.exec(stmt).first()
    if not member:
        raise ValueError("用户不在该群组中")
    
    # 使用兑换码，更新用户余额
    try:
        # 获取群组信息
        stmt = select(Group).where(Group.id == group_id)
        group = session.exec(stmt).first()
        group_name = group.name if group else "未知群组"
        
        # 更新兑换码状态
        code.is_used = True
        code.used_at = datetime.utcnow()
        code.used_by = user_id
        code.used_in_group = group_id
        
        # 更新用户在群组中的余额
        member = update_group_member_balance(session, user_id, group_id, code.amount)
        
        session.commit()
        
        return {
            "success": True,
            "message": "兑换码使用成功",
            "amount": code.amount,
            "group_name": group_name,
            "new_balance": member.balance
        }
    except Exception as e:
        session.rollback()
        raise ValueError(f"使用兑换码时出错: {str(e)}")

def get_all_codes(session: Session) -> List[dict]:
    """获取所有兑换码（管理员功能）
    
    Args:
        session: 数据库会话
    
    Returns:
        List[dict]: 所有兑换码的列表（不包含原始兑换码）
    """
    codes = session.exec(select(Code)).all()
    
    # 转换为字典列表，不包含敏感信息
    result = []
    for code in codes:
        result.append({
            "id": code.id,
            "code_prefix": code.code_prefix,  # 只显示前缀，隐藏后半部分
            "amount": code.amount,
            "is_used": code.is_used,
            "created_by": code.created_by,
            "created_at": code.created_at,
            "expires_at": code.expires_at,
            "used_at": code.used_at,
            "used_by": code.used_by,
            "used_in_group": code.used_in_group
        })
    
    return result

def get_user_codes(session: Session, user_id: int) -> List[dict]:
    """获取用户生成的所有兑换码
    
    Args:
        session: 数据库会话
        user_id: 用户ID
    
    Returns:
        List[dict]: 用户生成的兑换码列表（不包含原始兑换码）
    """
    codes = session.exec(select(Code).where(Code.created_by == user_id)).all()
    
    # 转换为字典列表，不包含敏感信息
    result = []
    for code in codes:
        result.append({
            "id": code.id,
            "code_prefix": code.code_prefix,  # 只显示前缀，隐藏后半部分
            "amount": code.amount,
            "is_used": code.is_used,
            "created_by": code.created_by,
            "created_at": code.created_at,
            "expires_at": code.expires_at,
            "used_at": code.used_at,
            "used_by": code.used_by,
            "used_in_group": code.used_in_group
        })
    
    return result

def get_used_codes(session: Session, used_by: int = None) -> List[dict]:
    """获取已使用的兑换码
    
    Args:
        session: 数据库会话
        used_by: 可选，指定使用兑换码的用户ID
    
    Returns:
        List[dict]: 已使用的兑换码列表（不包含原始兑换码）
    """
    query = select(Code).where(Code.is_used == True)
    if used_by:
        query = query.where(Code.used_by == used_by)
    
    codes = session.exec(query).all()
    
    # 转换为字典列表，不包含敏感信息
    result = []
    for code in codes:
        result.append({
            "id": code.id,
            "code_prefix": code.code_prefix + "****",  # 只显示前缀，隐藏后半部分
            "amount": code.amount,
            "is_used": code.is_used,
            "created_by": code.created_by,
            "created_at": code.created_at,
            "expires_at": code.expires_at,
            "used_at": code.used_at,
            "used_by": code.used_by,
            "used_in_group": code.used_in_group
        })
    
    return result
