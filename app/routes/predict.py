import uuid
import json
import datetime
import pika
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.config import get_settings
from app.schemas.predict import PredictionRequest
from app.services.crud.auth_service import get_current_user
from app.models.user import User
from app.services.crud import wallet_service as ws

# Импорты для транзакций
from app.services.crud.transaction_service import execute_transaction
from app.models.wallet import Wallet

logger = logging.getLogger(__name__)
settings = get_settings()
predict_router = APIRouter()

@predict_router.post("/")
async def predict(
    data: PredictionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Получение кошелька
    wallet = await ws.get_wallet_by_user_id(current_user.id, session)
    
    # Если кошелька нет, то создаем его и коммитим в базу (commit)
    if not wallet:
        logger.info(f"Auto-creating wallet for user {current_user.id}")
        wallet = Wallet(user_id=current_user.id, balance=0.0)
        session.add(wallet)
        await session.commit()  # Фиксируем, чтобы execute_transaction его нашел 
        await session.refresh(wallet)
    
    # Проверка баланса
    PREDICT_COST = 100.0
    if wallet.balance < PREDICT_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail=f"Недостаточно средств. Нужно: {PREDICT_COST}$, на балансе: {wallet.balance}$"
        )

    # Списание средств
    try:
        await execute_transaction(
            wallet_id=current_user.id,
            amount=PREDICT_COST,
            tx_type="debit",
            session=session
        )
    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обработки платежа"
        )

    # Подготовка задачи
    task_id = str(uuid.uuid4())
    message = {
        "task_id": task_id,
        "user_id": str(current_user.id),
        "features": data.features.dict(),
        "model": data.model_id or "Career Path Pro",
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        # Отправка в RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue='ml_tasks', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='ml_tasks',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()

        return {
            "task_id": task_id, 
            "status": "queued",
            "message": f"Оплачено {PREDICT_COST}$. Задача в очереди."
        }

    except Exception as e:
        # Возврат средств при ошибке RabbitMQ
        logger.error(f"RabbitMQ error: {e}. Refunding user {current_user.id}...")
        try:
            await execute_transaction(
                wallet_id=current_user.id,
                amount=PREDICT_COST,
                tx_type="credit",
                session=session
            )
            refund_info = "Средства автоматически вернулись на баланс."
        except Exception as refund_error:
            logger.critical(f"REFUND FAILED: {refund_error}")
            refund_info = "Сбой возврата. Пожалуйста, напишите в техподдержку."

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Сбой отправки задачи. {refund_info}"
        )