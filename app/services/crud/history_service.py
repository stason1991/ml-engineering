from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.history import PredictionHistory
from uuid import UUID
from typing import Sequence

async def get_history_by_user(user_id: UUID, session: AsyncSession) -> Sequence[PredictionHistory]:
  query = select(PredictionHistory).filter(PredictionHistory.user_id == user_id)
  result = await session.execute(query)
  return result.scalars().all()

async def add_history_entry(entry: PredictionHistory, session: AsyncSession) -> None:
  session.add(entry)
  await session.commit()

async def delete_history_by_user(user_id: UUID, session: AsyncSession) -> None:
  from sqlalchemy import delete
  await session.execute(delete(PredictionHistory).where(PredictionHistory.user_id == user_id))
  await session.commit()
