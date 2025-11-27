from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    public_info: Optional[str] = None
    password: Optional[str] = Field(default=None)  # 添加密码字段
    created_codes: List["Code"] = Relationship(back_populates="creator", sa_relationship_kwargs={'foreign_keys': 'Code.created_by'})
    used_codes: List["Code"] = Relationship(back_populates="user", sa_relationship_kwargs={'foreign_keys': 'Code.used_by'})


class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    used_codes: List["Code"] = Relationship(back_populates="group", sa_relationship_kwargs={'foreign_keys': 'Code.used_in_group'})


class GroupMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    group_id: int = Field(foreign_key="group.id", index=True)
    balance: float = 0.0  # 用户在该群组的余额
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 确保每个用户在一个群组中只有一条记录
    __table_args__ = ({
        "sqlite_autoincrement": True,
    },)


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: Optional[int] = Field(foreign_key="group.id", index=True)
    payer_id: int = Field(foreign_key="user.id")
    total_amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Code(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code_hash: str = Field(unique=True, index=True, nullable=False)  # 存储兑换码的哈希值
    code_salt: str = Field(nullable=False)  # 存储生成哈希时使用的盐值
    code_prefix: str = Field(max_length=6, nullable=False)  # 存储兑换码前缀（用于展示）
    amount: float
    is_used: bool = False
    created_by: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)  # 兑换码过期时间
    used_at: Optional[datetime] = None
    used_by: Optional[int] = Field(foreign_key="user.id", default=None)
    used_in_group: Optional[int] = Field(foreign_key="group.id", default=None)
    
    # 关系
    creator: "User" = Relationship(back_populates="created_codes", sa_relationship_kwargs={'foreign_keys': 'Code.created_by'})
    user: "User" = Relationship(back_populates="used_codes", sa_relationship_kwargs={'foreign_keys': 'Code.used_by'})
    group: "Group" = Relationship(back_populates="used_codes", sa_relationship_kwargs={'foreign_keys': 'Code.used_in_group'})


class TransactionParticipant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    share_amount: float  # 应付金额
    paid_amount: float = 0.0  # 实际付款
    settled: bool = False
