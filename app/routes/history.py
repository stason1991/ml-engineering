from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from models.history import PredictionHistory
from services.crud import history_service as service
from database.database import get_session
from schemas.history import HistoryCreate, HistoryResponse

history_router = APIRouter()

@history_router.get("/{user_id}", response_model=List[HistoryResponse])
async def read_user_history(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Получить всю историю предсказаний для конкретного пользователя"""
    return await service.get_history_by_user(user_id, session)

@history_router.post("/", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_history_record(
    data: HistoryCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Добавить новую запись в историю (результат модели)"""
    new_entry = PredictionHistory(
        user_id=data.user_id,
        result=data.result,
        data_snapshot=data.data_snapshot
    )
    await service.add_history_entry(new_entry, session)
    return new_entry

@history_router.delete("/{user_id}")
async def clear_user_history(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Полностью удалить историю предсказаний для пользователя"""
    history = await service.get_history_by_user(user_id, session)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"История для пользователя {user_id} не найдена"
        )
    
    await service.delete_history_by_user(user_id, session)
    return {"status": "success", "message": f"История пользователя {user_id} очищена"}