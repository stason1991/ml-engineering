from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.centroid import Centroid
from app.services.crud import centroid_service as service
from app.database.database import get_session
from app.schemas.centroid import CentroidCreate, CentroidResponse

centroid_router = APIRouter()

@centroid_router.get("/", response_model=List[CentroidResponse])
async def read_all_centroids(
    session: AsyncSession = Depends(get_session)
):
    """Получить список всех центроидов"""
    return await service.get_all_centroids(session)

@centroid_router.get("/{id}", response_model=CentroidResponse)
async def read_centroid(
    id: int, 
    session: AsyncSession = Depends(get_session)
):
    """Получить данные конкретного центроида по ID"""
    centroid = await service.get_centroid_by_id(id, session)
    if not centroid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Центроид с ID {id} не найден"
        )
    return centroid

@centroid_router.post("/", response_model=CentroidResponse, status_code=status.HTTP_201_CREATED)
async def create_new_centroid(
    data: CentroidCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Создать новый центроид и привязать его к модели по model_id"""
    new_centroid = Centroid(
        name=data.name, 
        model_id=data.model_id
    )
    return await service.create_centroid(new_centroid, session)

@centroid_router.patch("/{id}", response_model=CentroidResponse)
async def update_centroid_name_route(
    id: int, 
    name: str, 
    session: AsyncSession = Depends(get_session)
):
    """Обновить название существующего центроида"""
    updated = await service.update_centroid_name(id, name, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Центроид с ID {id} не найден"
        )
    return updated

@centroid_router.delete("/{id}")
async def delete_single_centroid(
    id: int, 
    session: AsyncSession = Depends(get_session)
):
    """Удалить центроид по ID"""
    try:
        await service.delete_centroid_by_id(id, session)
        return {"status": "success", "message": f"Центроид {id} удален"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@centroid_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_centroids_data(
    session: AsyncSession = Depends(get_session)
):
    """Полная очистка всех центроидов"""
    await service.delete_all_centroids(session)
    return None
