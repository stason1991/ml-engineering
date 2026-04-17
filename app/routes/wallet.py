from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models.wallet import Wallet
from services.crud import wallet_service as service
from database.database import get_session
from schemas.wallet import WalletCreate, WalletUpdate, WalletResponse

wallet_router = APIRouter()

@wallet_router.get("/{user_id}", response_model=WalletResponse)
async def read_wallet(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Получить информацию о кошельке пользователя"""
    wallet = await service.get_wallet_by_user_id(user_id, session)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Кошелек для пользователя {user_id} не найден"
        )
    return wallet

@wallet_router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_new_wallet(
    data: WalletCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Создать новый кошелек для пользователя"""
    # Проверка на существование кошелька
    existing = await service.get_wallet_by_user_id(data.user_id, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Кошелек для этого пользователя уже существует"
        )
    
    new_wallet = Wallet(user_id=data.user_id, balance=data.balance)
    return await service.create_wallet(new_wallet, session)

@wallet_router.patch("/{user_id}", response_model=WalletResponse)
async def update_balance(
    user_id: UUID, 
    data: WalletUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Прямое обновление баланса кошелька"""
    try:
        updated = await service.update_wallet_balance(user_id, data.balance, session)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )

@wallet_router.delete("/{user_id}")
async def delete_wallet_data(
    user_id: UUID, 
    session: AsyncSession = Depends(get_session)
):
    """Удалить кошелек пользователя"""
    wallet = await service.get_wallet_by_user_id(user_id, session)
    if not wallet:
        raise HTTPException(status_code=404, detail="Кошелек не найден")
    
    await service.delete_wallet(user_id, session)
    return {"status": "success", "message": f"Кошелек пользователя {user_id} удален"}
