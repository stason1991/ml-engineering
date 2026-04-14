from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from services.crud import transaction_service as service
from database.database import get_session
from schemas.transaction import TransactionCreate, TransactionResponse

transaction_router = APIRouter()

@transaction_router.get("/", response_model=List[TransactionResponse])
async def read_all_transactions(
    session: AsyncSession = Depends(get_session)
):
    """Получить список всех транзакций в системе"""
    return await service.get_all_transactions(session)

@transaction_router.get("/wallet/{wallet_id}", response_model=List[TransactionResponse])
async def read_wallet_transactions(
    wallet_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Получить историю транзакций конкретного кошелька"""
    return await service.get_transactions_by_wallet(wallet_id, session)

@transaction_router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate, 
    session: AsyncSession = Depends(get_session)
):
    """
    Выполнить транзакцию (пополнение или списание).
    """
    try:
        transaction = await service.execute_transaction(
            wallet_id=data.wallet_id,
            amount=data.amount,
            tx_type=data.tx_type,
            session=session
        )
        return transaction
    except ValueError as e:
        # Ошибка: кошелек не найден или неверный тип
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ошибка при выполнении транзакции"
        )

@transaction_router.get("/{transaction_id}", response_model=TransactionResponse)
async def read_transaction(
    transaction_id: int, 
    session: AsyncSession = Depends(get_session)
):
    """Получить детали конкретной транзакции по ID"""
    tx = await service.get_transaction_by_id(transaction_id, session)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Транзакция {transaction_id} не найдена"
        )
    return tx

@transaction_router.delete("/wallet/{wallet_id}")
async def clear_wallet_history(
    wallet_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Удалить все транзакции кошелька"""
    await service.delete_wallet_transactions(wallet_id, session)
    return {"status": "success", "message": f"История кошелька {wallet_id} очищена"}
