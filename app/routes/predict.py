import uuid
import json
import datetime
import pika
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.config import get_settings
from app.schemas.predict import PredictionRequest
from app.services.crud.auth_service import get_current_user
from app.models.user import User

settings = get_settings()
predict_router = APIRouter()

@predict_router.post("/")
async def predict(
    data: PredictionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Сценарий:
    1. Принимаем данные сотрудника (82 признака)
    2. Генерируем task_id
    3. Отправляем задачу в RabbitMQ для Worker
    4. Возвращаем клиенту ID задачи
    """
    task_id = str(uuid.uuid4())
    
    # Формируем сообщение
    message = {
        "task_id": task_id,
        "features": data.features.dict(),
        "model": data.model_id or "Career Path Pro",
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        # Подключение к RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()
        
        # Объявление очереди (на случай, если она еще не создана)
        channel.queue_declare(queue='ml_tasks', durable=True)
        
        # Публикация сообщения
        channel.basic_publish(
            exchange='',
            routing_key='ml_tasks',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Делает сообщение устойчивым к сбоям
            )
        )
        connection.close()

        # Возвращаем ответ сразу
        return {
            "task_id": task_id,
            "status": "queued",
            "message": "Задача успешно поставлена в очередь"
        }

    except Exception as e:
        # Возвращаем ошибку, елси брокер недоступен
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка брокера сообщений: {str(e)}"
        )