from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.centroid import Centroid

async def get_all_centroids(session: AsyncSession) -> List[Centroid]:
    result = await session.execute(select(Centroid))
    return list(result.scalars().all())

async def get_centroid_by_id(id: int, session: AsyncSession) -> Optional[Centroid]:
    """Найти центроид по его ID"""
    return await session.get(Centroid, id)

async def create_centroid(new_centroid: Centroid, session: AsyncSession) -> Centroid:
    session.add(new_centroid)
    await session.commit()
    await session.refresh(new_centroid)
    return new_centroid

async def update_centroid_name(id: int, new_name: str, session: AsyncSession) -> Optional[Centroid]:
    centroid = await get_centroid_by_id(id, session)
    if centroid:
        centroid.name = new_name
        await session.commit()
        await session.refresh(centroid)
    return centroid

async def delete_centroid_by_id(id: int, session: AsyncSession) -> None:
    centroid = await get_centroid_by_id(id, session) # Используем новый метод
    if centroid:
        await session.delete(centroid)
        await session.commit()
    else:
        raise Exception(f"Centroid with id {id} not found")

async def delete_all_centroids(session: AsyncSession) -> None:
    await session.execute(delete(Centroid))
    await session.commit()