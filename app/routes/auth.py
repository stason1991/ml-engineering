from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.database.database import get_session
from app.schemas.auth import LoginRequest, AuthResponse
from app.services.crud import auth_service

auth_router = APIRouter()

@auth_router.post("/login", response_model=AuthResponse)
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Вход в систему"""
    user = await auth_service.authenticate_user(data.username, data.password, session)

    access_token = auth_service.create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
