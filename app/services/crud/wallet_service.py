from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wallet import Wallet
from app.services.crud.transaction_service import execute_transaction

async def get_wallet_by_user_id(user_id: UUID, session: AsyncSession) -> Optional[Wallet]:
  result = await session.execute(select(Wallet).where(Wallet.user_id == user_id))
  return result.scalar_one_or_none()

async def create_wallet(new_wallet: Wallet, session: AsyncSession) -> Wallet:
  session.add(new_wallet)
  await session.commit()
  await session.refresh(new_wallet)
  return new_wallet

async def update_wallet_balance(user_id: UUID, amount: float, session: AsyncSession) -> Wallet:
    await execute_transaction(
        wallet_id=user_id,
        amount=float(amount),
        tx_type="credit",
        session=session
    )
    
    # Возвращаем обновленный кошелек
    return await get_wallet_by_user_id(user_id, session)

async def delete_wallet(user_id: UUID, session: AsyncSession) -> None:
  wallet = await get_wallet_by_user_id(user_id, session)
  if wallet:
    await session.delete(wallet)
    await session.commit()
