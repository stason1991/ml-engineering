from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UserCreate(BaseModel):
    login: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserMe(BaseModel):
    id: UUID
    login: str
    
    class Config:
        from_attributes = True

class InfoResponse(BaseModel):
    message: str
    user_id: Optional[UUID] = None