from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
  from app.models.user import User
  from app.models.transaction import Transaction

class Wallet(Base):
  __tablename__ = "wallets"

  id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
  balance: Mapped[float] = mapped_column(Float, default=0.0)

  user: Mapped["User"] = relationship(back_populates="wallet")
  transactions: Mapped[List["Transaction"]] = relationship(back_populates="wallet")