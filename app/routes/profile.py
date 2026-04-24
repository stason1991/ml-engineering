from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.models.profile import BankEmployeeProfile
from app.services.crud import profile_service as service
from app.database.database import get_session
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

profile_router = APIRouter()

@profile_router.get("/{user_id}", response_model=ProfileResponse)
async def read_profile(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    profile = await service.get_profile_by_user_id(user_id, session)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Профиль для пользователя {user_id} не найден"
        )
    return profile

@profile_router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_new_profile(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_session)
):
    existing = await service.get_profile_by_user_id(data.user_id, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Профиль уже существует"
        )
    
    new_profile = BankEmployeeProfile(user_id=data.user_id, attributes=data.attributes)
    return await service.create_profile(new_profile, session)

@profile_router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: UUID, 
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_session)
):
    try:
        updated = await service.update_profile_attributes(user_id, data.attributes, session)
        return updated
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@profile_router.delete("/{user_id}")
async def delete_profile_data(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    profile = await service.get_profile_by_user_id(user_id, session)
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    await service.delete_profile(user_id, session)
    return {"status": "success", "message": f"Профиль {user_id} удален"}
