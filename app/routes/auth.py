from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from schemas.auth import LoginRequest, AuthResponse
from services.crud import auth_service

auth_router = APIRouter()

@auth_router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """Вход в систему"""
    user = await auth_service.authenticate_user(data.login, data.password, session)
    
    return {
        "status": "success",
        "user_id": str(user.id),
        "message": f"Добро пожаловать, {user.login}!"
    }
