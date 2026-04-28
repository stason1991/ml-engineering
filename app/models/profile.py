from datetime import datetime
from uuid import UUID
from typing import Dict, Any, TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
  from app.models.user import User

class BankEmployeeProfile(Base):
  __tablename__ = "employee_profiles"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
  attributes: Mapped[Dict[str, Any]] = mapped_column(JSON)

  user: Mapped["User"] = relationship(back_populates="profile")
