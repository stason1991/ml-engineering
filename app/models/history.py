from sqlalchemy import ForeignKey, String, Float, DateTime, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import TYPE_CHECKING, List
from .base import Base

if TYPE_CHECKING:
    from .user import User

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Уникальный ID задачи из RabbitMQ
    task_id: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    
    # Ссылка на пользователя
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Результат классификации (название роли)
    result: Mapped[str] = mapped_column(String, nullable=False)
    
    # Уверенность модели (0.0 - 1.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    
    # ID воркера, который выполнил расчет
    worker_id: Mapped[str] = mapped_column(String, nullable=True)
    
    # Снапшот входных данных (82 признака)
    data_snapshot: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=True)
    
    # Время создания записи
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь с пользователем
    user: Mapped["User"] = relationship(back_populates="history")

    def __repr__(self):
        return f"<PredictionHistory(task={self.task_id}, res={self.result}, conf={self.confidence})>"