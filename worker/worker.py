import pika
import json
import joblib
import numpy as np
import os
import asyncio
import time
import logging
from sklearn.metrics.pairwise import cosine_distances
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.database.database import settings, init_db
from app.models.history import PredictionHistory
from app.models.wallet import Wallet

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_NAME = 'ml_tasks'
MODEL_PATH = 'model_assets.pkl'

# Загрузка ML-модели при старте
logger.info(f"[*] Загрузка модели из {MODEL_PATH}...")
assets = joblib.load(MODEL_PATH)
FEATURE_MAPPING = assets["feature_names"]
scaler = assets["scaler"]
centroids = assets["centroids"]

async def save_to_db(result_data, raw_vector):
    """
    Сохранение результата прогноза в БД без баланса
    """
    logger.info(f"DEBUG WORKER: Сохраняю результат задачи {result_data['task_id']}")
    
    temp_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=False)
    temp_session_factory = async_sessionmaker(
        bind=temp_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )

    async with temp_session_factory() as session:
        try:
            # Создаем запись в истории прогнозов
            history_entry = PredictionHistory(
                task_id=result_data['task_id'],
                user_id=result_data['user_id'],
                result=result_data['prediction'],
                confidence=result_data['confidence'],
                worker_id=result_data['worker_id'],
                data_snapshot=raw_vector
            )
            session.add(history_entry)
            
            # Сохраняем результат в базе
            await session.commit()
            logger.info(f"[DB] Результат задачи {result_data['task_id']} успешно сохранен.")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"[DB Error] Ошибка сохранения: {e}")
            raise e
        finally:
            await session.close()
    
    await temp_engine.dispose()

def process_task(ch, method, properties, body):
    try:
        data = json.loads(body)
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        features_dict = data.get("features")

        # 1. Подготовка вектора
        raw_vector = [float(features_dict.get(feat, 0)) for feat in FEATURE_MAPPING]
        vector_np = np.array(raw_vector).reshape(1, -1)

        # 2. ML-расчет (Cosine distance)
        scaled_vector = scaler.transform(vector_np)
        distances = {}
        for role, center_vec in centroids.items():
            dist_matrix = cosine_distances(scaled_vector, center_vec)
            distances[role] = float(dist_matrix[0][0])
        
        best_role = min(distances, key=distances.get)
        confidence = 1.0 - distances[best_role]

        # 3. Формирование ответа
        result_payload = {
            "task_id": task_id,
            "user_id": user_id,
            "prediction": best_role,
            "confidence": round(confidence, 4),
            "worker_id": f"worker-{os.getpid()}",
            "status": "success"
        }

        # 4. Сохранение в БД (только история прогнозов)
        asyncio.run(save_to_db(result_payload, raw_vector))

        # 5. Подтверждение RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"[V] Выполнено: {best_role} для юзера {user_id}")

    except Exception as e:
        logger.error(f"[X] Ошибка обработки задачи: {str(e)}")
        # Возвращаем задачу в очередь при ошибке
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    time.sleep(2)
    logger.info("[*] Инициализация БД для воркера...")
    asyncio.run(init_db())

    logger.info(f"[*] Подключение к RabbitMQ: {RABBITMQ_HOST}...")
    
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            break
        except pika.exceptions.AMQPConnectionError:
            logger.info(f"[!] Ожидание RabbitMQ... ({i+1}/10)")
            time.sleep(5)
    else:
        logger.error("[X] Критическая ошибка: RabbitMQ недоступен.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_task)

    logger.info(f"[*] Воркер успешно запущен. PID: {os.getpid()}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()

if __name__ == "__main__":
    start_worker()