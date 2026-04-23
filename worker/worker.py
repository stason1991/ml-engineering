import pika
import json
import joblib
import numpy as np
import os
import asyncio
import time
from sklearn.metrics.pairwise import cosine_distances
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database.database import settings, init_db
from app.models.history import PredictionHistory
from app.models.wallet import Wallet

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_NAME = 'ml_tasks'
MODEL_PATH = 'model_assets.pkl'

# Загрузка прототипа ML-модели при старте процесса
print(f"[*] Загрузка модели из {MODEL_PATH}...")
assets = joblib.load(MODEL_PATH)
FEATURE_MAPPING = assets["feature_names"]
scaler = assets["scaler"]
centroids = assets["centroids"]

async def save_to_db(result_data, raw_vector):
    """
    Асинхронное сохранение
    """
    print(f"DEBUG WORKER: Сохраняю задачу {result_data['task_id']} для юзера: {result_data.get('user_id')}")
    # Временный движок для текущей транзакции
    temp_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=False)
    temp_session_factory = async_sessionmaker(
        bind=temp_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )

    async with temp_session_factory() as session:
        try:
            history_entry = PredictionHistory(
                task_id=result_data['task_id'],
                user_id=result_data['user_id'],
                result=result_data['prediction'],
                confidence=result_data['confidence'],
                worker_id=result_data['worker_id'],
                data_snapshot=raw_vector
            )
            session.add(history_entry)

            from sqlalchemy import select
            # Ищем кошелек
            query = select(Wallet).filter_by(user_id=result_data['user_id'])
            result = await session.execute(query)
            wallet = result.scalar_one_or_none()

            if wallet:
                cost = 1000.0 # Цена
                wallet.balance -= cost
                print(f"[WALLET] Списано {cost} с кошелька {wallet.id}. Новый баланс: {wallet.balance}")

            await session.commit()
            print(f"[DB] Задача {result_data['task_id']} сохранена, баланс обновлен.")
            
        except Exception as e:
            await session.rollback()
            print(f"[DB Error] Ошибка: {e}")


            await session.commit()
            print(f"[DB] Задача {result_data['task_id']} успешно сохранена.")
        except Exception as e:
            await session.rollback()
            print(f"[DB Error] Ошибка сохранения: {e}")
            raise e
        finally:
            await session.close()
    
    # Закрываем временный движок
    await temp_engine.dispose()

def process_task(ch, method, properties, body):
    try:
        data = json.loads(body)
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        features_dict = data.get("features")

        # Создание вектора
        raw_vector = [float(features_dict.get(feat, 0)) for feat in FEATURE_MAPPING]
        vector_np = np.array(raw_vector).reshape(1, -1)

        # Расчет
        scaled_vector = scaler.transform(vector_np)
        distances = {}
        for role, center_vec in centroids.items():
            dist_matrix = cosine_distances(scaled_vector, center_vec)
            distances[role] = float(dist_matrix[0][0])
        
        best_role = min(distances, key=distances.get)
        confidence = 1.0 - distances[best_role]

        # Результат
        result_payload = {
            "task_id": task_id,
            "user_id": user_id,
            "prediction": best_role,
            "confidence": round(confidence, 4),
            "worker_id": f"worker-{os.getpid()}",
            "status": "success"
        }

        # Сохранение (Синхронный запуск асинхронной функции)
        asyncio.run(save_to_db(result_payload, raw_vector))

        # Подтверждение
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[V] Выполнено: {best_role} (уверенность: {result_payload['confidence']})")

    except Exception as e:
        print(f"[X] Ошибка обработки: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    time.sleep(2)
    print("[*] Проверка структуры БД...")
    asyncio.run(init_db())

    print(f"[*] Подключение к RabbitMQ: {RABBITMQ_HOST}...")
    # Цикл ожидания RabbitMQ
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"[!] Ожидание RabbitMQ... ({i+1}/10)")
            time.sleep(5)
    else:
        print("[X] Не удалось подключиться к RabbitMQ.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_task)

    print(f"[*] Воркер запущен (PID: {os.getpid()}). Ожидание задач...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()

if __name__ == "__main__":
    start_worker()