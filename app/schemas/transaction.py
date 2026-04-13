from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    wallet_id: UUID
    amount: float = Field(..., gt=0, description="Сумма транзакции")

class TransactionCreate(TransactionBase):
    tx_type: str = Field(..., pattern="^(debit|credit)$", description="Тип: debit или credit")

class TransactionResponse(TransactionBase):
    id: int
    tx_type: str
    timestamp: datetime

    class Config:
        from_attributes = True
