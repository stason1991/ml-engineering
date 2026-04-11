from uuid import UUID, uuid4
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
  from .wallet import Wallet
  from .profile import BankEmployeeProfile
  from .history import PredictionHistory

class User(Base):
  __tablename__ = "users"

  id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
  login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  password_hash: Mapped[str] = mapped_column(String, nullable=False)

  wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)
  profile: Mapped["BankEmployeeProfile"] = relationship(back_populates="user", uselist=False)
  history: Mapped[List["PredictionHistory"]] = relationship(back_populates="user")
