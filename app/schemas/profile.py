from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any

class ProfileBase(BaseModel):
    attributes: Dict[str, Any] = Field(default={}, description="Характеристики сотрудника")

class ProfileCreate(ProfileBase):
    user_id: UUID

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: UUID

    class Config:
        from_attributes = True
