from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class TransactionBase(BaseModel):
    wallet_id: UUID
    amount: float = Field(..., gt=0, description="Сумма транзакции")

class TransactionCreate(TransactionBase):
    tx_type: TransactionType = Field(..., description="Тип транзакции")

class TransactionResponse(TransactionBase):
    id: int
    tx_type: str
    timestamp: datetime

    class Config:
        from_attributes = True
