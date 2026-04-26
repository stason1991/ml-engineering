from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class HistoryBase(BaseModel):
    result: str = Field(..., description="Результат предсказания")
    data_snapshot: Optional[List[float]] = Field(None, description="Вектор")
    # ДОБАВЛЯЕМ ЭТИ ПОЛЯ, чтобы они не терялись при передаче на фронтенд
    confidence: Optional[float] = Field(0.0, description="Точность/Уверенность модели")
    task_id: Optional[str] = Field(None, description="ID задачи")

class HistoryCreate(HistoryBase):
    user_id: UUID

class HistoryResponse(HistoryBase):
    id: int
    user_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)