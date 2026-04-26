from uuid import UUID
from typing import List, Optional
import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction, DebitTransaction, CreditTransaction
from app.models.wallet import Wallet

logger = logging.getLogger(__name__)

async def execute_transaction(
    wallet_id: UUID, 
    amount: float, 
    tx_type: str, 
    session: AsyncSession
) -> Transaction:
    """Создает транзакцию и обновляет баланс кошелька."""
    # 1. Находим кошелек строго по user_id (так как wallet_id из фронта это UUID юзера)
    result = await session.execute(
        select(Wallet).where(Wallet.user_id == wallet_id)
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        logger.error(f"Transaction failed: Wallet for user {wallet_id} not found")
        raise ValueError(f"Wallet with user_id {wallet_id} not found")

    # 2. Создаем объект транзакции
    target_id = wallet.id 

    if tx_type == "debit":
        new_tx = DebitTransaction(wallet_id=target_id, amount=amount)
    elif tx_type == "credit":
        new_tx = CreditTransaction(wallet_id=target_id, amount=amount)
    else:
        raise ValueError("Invalid transaction type. Use 'debit' or 'credit'.")

    # 3. Применяем логику изменения баланса (new_tx.apply изменяет wallet.balance)
    new_tx.apply(wallet)

    # 4. Явно добавляем оба объекта в сессию
    session.add(wallet)
    session.add(new_tx)

    # 5. Сохраняем изменения
    try:
        await session.flush()
        await session.commit()
        await session.refresh(new_tx)
        logger.info(f"Transaction success: {tx_type} {amount} for user {wallet_id}")
        return new_tx
    except Exception as e:
        await session.rollback()
        logger.error(f"DATABASE ERROR during transaction: {str(e)}")
        raise e

async def get_transactions_by_wallet(wallet_id: UUID, session: AsyncSession) -> List[Transaction]:
    """
    Получает историю. 
    Wallet_id здесь — это UUID пользователя из сессии Django.
    """
    # Находим внутренний ID кошелька этого пользователя
    res = await session.execute(select(Wallet).where(Wallet.user_id == wallet_id))
    wallet = res.scalar_one_or_none()
    
    if not wallet:
        return []

    # Ищем транзакции, привязанные к этому кошельку
    result = await session.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.timestamp.desc())
    )
    return list(result.scalars().all())

async def get_all_transactions(session: AsyncSession) -> List[Transaction]:
    result = await session.execute(select(Transaction).order_by(Transaction.timestamp.desc()))
    return list(result.scalars().all())

async def get_transaction_by_id(transaction_id: int, session: AsyncSession) -> Optional[Transaction]:
    return await session.get(Transaction, transaction_id)

async def delete_transaction_by_id(transaction_id: int, session: AsyncSession) -> None:
    tx = await session.get(Transaction, transaction_id)
    if tx:
        await session.delete(tx)
        await session.commit()

async def delete_wallet_transactions(wallet_id: UUID, session: AsyncSession) -> None:
    # Здесь wallet_id может быть UUID пользователя, нужно найти Wallet.id
    res = await session.execute(select(Wallet).where(Wallet.user_id == wallet_id))
    wallet = res.scalar_one_or_none()
    if wallet:
        await session.execute(delete(Transaction).where(Transaction.wallet_id == wallet.id))
        await session.commit()

async def init_demo_transaction(wallet_id: UUID, session: AsyncSession):
    """Демо-транзакция при старте"""
    res = await session.execute(select(Wallet).where(Wallet.user_id == wallet_id))
    wallet = res.scalar_one_or_none()
    if wallet:
        check = await session.execute(select(Transaction).where(Transaction.wallet_id == wallet.id))
        if not check.scalars().first():
            await execute_transaction(wallet_id, 1000.0, "credit", session)

async def create_transaction(new_tx: Transaction, session: AsyncSession) -> Transaction:
    session.add(new_tx)
    await session.commit()
    await session.refresh(new_tx)
    return new_tx