from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
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
    # Привязываем tx_type к полю 'type' из базы данных
    tx_type: str = Field(..., alias="type")
    timestamp: datetime

    # Используем только современный способ настройки для Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
