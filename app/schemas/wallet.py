from pydantic import BaseModel, Field
from uuid import UUID

class WalletBase(BaseModel):
    balance: float = Field(0.0, ge=0, description="Баланс кошелька")

class WalletCreate(WalletBase):
    user_id: UUID

class WalletUpdate(BaseModel):
    balance: float = Field(..., ge=0)

class WalletResponse(WalletBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
