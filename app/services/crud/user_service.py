from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from sqlalchemy.orm import joinedload

async def get_all_users(session: AsyncSession) -> List[User]:
  result = await session.execute(select(User).options(joinedload(User.wallet)))
  return list(result.scalars().all())

async def get_user_by_id(user_id: UUID, session: AsyncSession) -> Optional[User]:
  return await session.get(User, user_id)

async def create_user(new_user: User, session: AsyncSession) -> User:
  session.add(new_user)
  await session.commit()
  await session.refresh(new_user)
  return new_user

async def update_user_password(user_id: UUID, new_hash: str, session: AsyncSession) -> Optional[User]:
  user = await session.get(User, user_id)
  if user:
    user.password_hash = new_hash
    await session.commit()
    await session.refresh(user)
  return user

async def delete_user_by_id(user_id: UUID, session: AsyncSession) -> None:
  user = await session.get(User, user_id)
  if user:
    await session.delete(user)
    await session.commit()
  else:
    raise Exception(f"User {user_id} not found")
