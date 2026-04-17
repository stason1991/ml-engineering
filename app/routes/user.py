from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from models.user import User
from services.crud import user_service as service
from database.database import get_session
from schemas.user import UserCreate, UserResponse, UserUpdatePassword

user_router = APIRouter()

@user_router.get("/", response_model=List[UserResponse])
async def read_all_users(
    session: AsyncSession = Depends(get_session)
):
    """Получить список всех пользователей с их кошельками"""
    return await service.get_all_users(session)

@user_router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Получить данные пользователя по UUID"""
    user = await service.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Пользователь {user_id} не найден"
        )
    return user

@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    data: UserCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Регистрация нового пользователя"""
    new_user = User(
        login=data.login, 
        password_hash=f"hash_{data.password}" #условно захешировали
    )
    return await service.create_user(new_user, session)

@user_router.patch("/{user_id}/password")
async def change_password(
    user_id: UUID, 
    data: UserUpdatePassword, 
    session: AsyncSession = Depends(get_session)
):
    """Обновить пароль пользователя"""
    #условно захешировали
    new_hash = f"hash_{data.new_password}"
    updated = await service.update_user_password(user_id, new_hash, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Пользователь {user_id} не найден"
        )
    return {"status": "success", "message": "Пароль успешно обновлен"}

@user_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Удалить пользователя"""
    try:
        await service.delete_user_by_id(user_id, session)
        return {"status": "success", "message": f"Пользователь {user_id} удален"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
