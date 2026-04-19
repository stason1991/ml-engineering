from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class HistoryBase(BaseModel):
    result: str = Field(..., description="Результат предсказания")
    data_snapshot: Optional[List[float]] = Field(None, description="Вектор, по которому было предсказание")

class HistoryCreate(HistoryBase):
    user_id: UUID

class HistoryResponse(HistoryBase):
    id: int
    user_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True