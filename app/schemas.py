from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# 用户创建模型
class CreateUser(BaseModel):
    name: str
    public_info: Optional[str] = None


# 群组创建模型
class CreateGroup(BaseModel):
    name: str
    member_ids: Optional[List[int]] = []


# 添加用户到群组
class AddUserToGroup(BaseModel):
    user_id: int
    group_id: Optional[int] = None
    initial_balance: float = 0.0


# 更新用户群组余额
class UpdateGroupBalance(BaseModel):
    user_id: int
    group_id: Optional[int] = None
    balance_change: float  # 余额变化量，可以是正数或负数


# 交易参与者模型（用于创建交易时指定参与者）
class ParticipantIn(BaseModel):
    user_id: int
    share_amount: Optional[float] = None  # AA模式下不需要指定，会自动计算
    paid_amount: float = 0.0


# 创建交易（AA模式）
class CreateTransaction(BaseModel):
    group_id: int
    payer_id: int
    total_amount: float
    description: Optional[str] = None
    participants: Optional[List[int]] = []  # 只需要提供参与者的用户ID列表，系统自动AA计算


# 群组成员信息
class GroupMemberOut(BaseModel):
    id: int
    user_id: int
    group_id: int
    balance: float
    joined_at: datetime
    user: Optional['UserOut'] = None  # 关联的用户信息

    class Config:
        from_attributes = True  # Pydantic V2使用from_attributes替代orm_mode


# 用于响应的通用模型（FastAPI 返回时会用到）
class UserOut(BaseModel):
    id: int
    name: str
    public_info: Optional[str]

    class Config:
        from_attributes = True  # Pydantic V2使用from_attributes替代orm_mode


class GroupOut(BaseModel):
    id: int
    name: str
    members: Optional[List[GroupMemberOut]] = []  # 包含群组所有成员信息

    class Config:
        from_attributes = True  # Pydantic V2使用from_attributes替代orm_mode


class TransactionParticipantOut(BaseModel):
    id: int
    user_id: int
    share_amount: float
    paid_amount: float
    settled: bool
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True  # Pydantic V2使用from_attributes替代orm_mode


class TransactionOut(BaseModel):
    id: int
    group_id: int
    payer_id: int
    total_amount: float
    description: Optional[str]
    created_at: datetime
    participants: List[TransactionParticipantOut]

    class Config:
        from_attributes = True  # Pydantic V2使用from_attributes替代orm_mode


# 解决循环引用
GroupMemberOut.model_rebuild()
