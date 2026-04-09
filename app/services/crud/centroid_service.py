from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.centroid import Centroid

async def get_all_centroids(session: AsyncSession) -> List[Centroid]:
  result = await session.execute(select(Centroid))
  return list(result.scalars().all())

async def create_centroid(new_centroid: Centroid, session: AsyncSession) -> Centroid:
  session.add(new_centroid)
  await session.commit()
  await session.refresh(new_centroid)
  return new_centroid

async def update_centroid_coords(id: int, coords: List[float], session: AsyncSession) -> Optional[Centroid]:
  centroid = await session.get(Centroid, id)
  if centroid:
    centroid.coordinates = coords
    await session.commit()
    await session.refresh(centroid)
  return centroid

async def delete_centroid_by_id(id: int, session: AsyncSession) -> None:
  centroid = await session.get(Centroid, id)
  if centroid:
    await session.delete(centroid)
    await session.commit()
  else:
    raise Exception(f"Centroid with id {id} not found")

async def delete_all_centroids(session: AsyncSession) -> None:
  await session.execute(delete(Centroid))
  await session.commit()
