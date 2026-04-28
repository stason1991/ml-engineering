from pydantic import BaseModel, Field
from typing import Optional

class MLModelBase(BaseModel):
    name: str = Field(..., description="Имя модели")
    description: Optional[str] = Field(None, description="Описание модели")

class MLModelCreate(MLModelBase):
    pass

class MLModelResponse(MLModelBase):
    id: int

    class Config:
        from_attributes = True