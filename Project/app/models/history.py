from datetime import datetime
from uuid import UUID
from typing import List
from sqlalchemy import ForeignKey, String, Float, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class PredictionHistory(Base):
  __tablename__ = "prediction_history"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
  result: Mapped[str] = mapped_column(String, nullable=False)
  data_snapshot: Mapped[List[float]] = mapped_column(ARRAY(Float))
  timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

  user: Mapped["User"] = relationship(back_populates="history")
