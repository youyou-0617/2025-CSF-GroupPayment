from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    public_info: Optional[str] = None


class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: Optional[int] = Field(foreign_key="group.id", index=True)
    payer_id: int = Field(foreign_key="user.id")
    total_amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransactionParticipant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    share_amount: float  # 应付金额
    paid_amount: float = 0.0  # 实际付款
    settled: bool = False
