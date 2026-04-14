from uuid import UUID
from typing import List, TYPE_CHECKING
from datetime import datetime  # Добавлен импорт
from sqlalchemy import ForeignKey, String, Float, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .user import User

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    result: Mapped[str] = mapped_column(String, nullable=False)
    data_snapshot: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь с пользователем
    user: Mapped["User"] = relationship(back_populates="history")