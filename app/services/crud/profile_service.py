from uuid import UUID
from typing import Optional, Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.profile import BankEmployeeProfile

async def get_profile_by_user_id(user_id: UUID, session: AsyncSession) -> Optional[BankEmployeeProfile]:
  result = await session.execute(select(BankEmployeeProfile).where(BankEmployeeProfile.user_id == user_id))
  return result.scalar_one_or_none()

async def create_profile(new_profile: BankEmployeeProfile, session: AsyncSession) -> BankEmployeeProfile:
  session.add(new_profile)
  await session.commit()
  await session.refresh(new_profile)
  return new_profile

async def update_profile_attributes(user_id: UUID, attributes: Dict[str, Any], session: AsyncSession) -> BankEmployeeProfile:
  profile = await get_profile_by_user_id(user_id, session)
  if profile:
    profile.attributes = attributes
    await session.commit()
    await session.refresh(profile)
    return profile
  raise Exception("Profile not found")

async def delete_profile(user_id: UUID, session: AsyncSession) -> None:
  profile = await get_profile_by_user_id(user_id, session)
  if profile:
    await session.delete(profile)
    await session.commit()
