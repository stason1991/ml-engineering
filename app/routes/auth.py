from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_session
from app.models.user import User
from app.schemas.auth import UserCreate, AuthResponse, UserMe, InfoResponse
from app.services.crud.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    get_password_hash
)

auth_router = APIRouter()

@auth_router.post("/register", response_model=InfoResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_session)
):
    """
    Регистрация нового пользователя
    """
    # Проверка логина
    query = select(User).where(User.login == user_data.login)
    result = await session.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )

    # Хешируем пароль
    new_user = User(
        login=user_data.login,
        password_hash=get_password_hash(user_data.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {"message": "Пользователь успешно зарегистрирован", "user_id": new_user.id}

@auth_router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """
    Вход в систему
    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    
    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@auth_router.get("/me", response_model=UserMe)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Личный кабинет
    """
    return current_user