from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from models.history import PredictionHistory
from models.user import User
from services.crud import history_service as service
from database.database import get_session
from schemas.history import HistoryResponse
from services.crud.auth_service import get_current_user


history_router = APIRouter()

@history_router.get("/{user_id}", response_model=List[HistoryResponse])
async def read_user_history(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Получить всю историю предсказаний для себя"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступен просмотр только своей истории"
        )
    return await service.get_history_by_user(user_id, session)

@history_router.delete("/{user_id}")
async def clear_user_history(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Полностью удалить историю для себя"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свою историю"
        )

    history = await service.get_history_by_user(user_id, session)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"История для пользователя {user_id} не найдена"
        )
    
    await service.delete_history_by_user(user_id, session)
    return {"status": "success", "message": f"История пользователя {user_id} очищена"}