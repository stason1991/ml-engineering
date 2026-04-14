from pydantic import BaseModel

class LoginRequest(BaseModel):
    login: str
    password: str

class AuthResponse(BaseModel):
    status: str
    user_id: str
    message: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"