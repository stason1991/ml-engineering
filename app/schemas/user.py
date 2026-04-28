from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль")

class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class UserUpdatePassword(BaseModel):
    new_password: str = Field(..., min_length=6)
