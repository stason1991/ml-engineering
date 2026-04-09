from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.transaction import Transaction, DebitTransaction, CreditTransaction
from models.wallet import Wallet

async def execute_transaction(
    wallet_id: UUID, 
    amount: float, 
    tx_type: str, 
    session: AsyncSession
) -> Transaction:
    """Создает транзакцию и обновляет баланс кошелька."""
    # Все строки ниже должны иметь отступ ровно 4 пробела
    wallet = await session.get(Wallet, wallet_id)
    if not wallet:
        raise ValueError(f"Wallet with id {wallet_id} not found")

    if tx_type == "debit":
        new_tx = DebitTransaction(wallet_id=wallet_id, amount=amount)
    elif tx_type == "credit":
        new_tx = CreditTransaction(wallet_id=wallet_id, amount=amount)
    else:
        raise ValueError("Invalid transaction type. Use 'debit' or 'credit'.")

    # Применяем логику изменения баланса
    new_tx.apply(wallet)

    session.add(new_tx)
    await session.commit()
    await session.refresh(new_tx)
    return new_tx

async def get_all_transactions(session: AsyncSession) -> List[Transaction]:
    result = await session.execute(select(Transaction).order_by(Transaction.timestamp.desc()))
    return list(result.scalars().all())

async def get_transactions_by_wallet(wallet_id: UUID, session: AsyncSession) -> List[Transaction]:
    result = await session.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet_id)
        .order_by(Transaction.timestamp.desc())
    )
    return list(result.scalars().all())

async def get_transaction_by_id(transaction_id: int, session: AsyncSession) -> Optional[Transaction]:
    return await session.get(Transaction, transaction_id)

async def delete_transaction_by_id(transaction_id: int, session: AsyncSession) -> None:
    tx = await session.get(Transaction, transaction_id)
    if tx:
        await session.delete(tx)
        await session.commit()

async def delete_wallet_transactions(wallet_id: UUID, session: AsyncSession) -> None:
    await session.execute(delete(Transaction).where(Transaction.wallet_id == wallet_id))
    await session.commit()

async def create_transaction(new_tx: Transaction, session: AsyncSession) -> Transaction:
    """Простое создание транзакции"""
    session.add(new_tx)
    await session.commit()
    await session.refresh(new_tx)
    return new_tx