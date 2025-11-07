from typing import Optional, List
from pydantic import BaseModel


# 用户创建模型
class CreateUser(BaseModel):
    name: str
    public_info: Optional[str] = None


# 群组创建模型
class CreateGroup(BaseModel):
    name: str


# 交易参与者模型（用于创建交易时指定每个人的分摊）
class ParticipantIn(BaseModel):
    user_id: int
    share_amount: float
    paid_amount: float = 0.0


# 创建交易
class CreateTransaction(BaseModel):
    group_id: int
    payer_id: int
    total_amount: float
    description: Optional[str] = None
    participants: List[ParticipantIn]


# 用于响应的通用模型（FastAPI 返回时会用到）
class UserOut(BaseModel):
    id: int
    name: str
    public_info: Optional[str]

    class Config:
        orm_mode = True


class GroupOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TransactionOut(BaseModel):
    id: int
    group_id: int
    payer_id: int
    total_amount: float
    description: Optional[str]
    participants: List[ParticipantIn]

    class Config:
        orm_mode = True
