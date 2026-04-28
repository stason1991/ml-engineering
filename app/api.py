from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user import user_router
from app.routes.profile import profile_router
from app.routes.history import history_router
from app.routes.wallet import wallet_router
from app.routes.transaction import transaction_router
from app.routes.ml_model import ml_model_router
from app.routes.centroid import centroid_router
from app.routes.predict import predict_router
from app.routes.auth import auth_router
from app.database.database import init_db
from app.database.config import get_settings
import uvicorn
import logging
import pika
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs/", 
        redoc_url="/api/redoc"
    )

    # Инициализация инструментатора, создание эндпоинта /metrics
    Instrumentator().instrument(app).expose(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Регистрация роутов
    app.include_router(user_router, prefix='/api/users', tags=['Users'])
    app.include_router(profile_router, prefix='/api/profiles', tags=['Profiles'])
    app.include_router(history_router, prefix='/api/history', tags=['History'])
    app.include_router(wallet_router, prefix='/api/wallets', tags=['Wallets'])
    app.include_router(transaction_router, prefix='/api/transactions', tags=['Transactions'])
    app.include_router(ml_model_router, prefix='/api/ml-models', tags=['ML Models'])
    app.include_router(centroid_router, prefix='/api/centroids', tags=['Centroids'])
    app.include_router(predict_router, prefix='/api/predict', tags=['Predict'])
    app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])

    return app

app = create_application()

@app.on_event("startup")
async def on_startup():
    try:
        logger.info("Initializing database...")
        await init_db()

        # Инициализация демо-данных и ML-моделей
        from app.services.crud.ml_model_service import setup_demo_data
        from app.database.database import async_session_factory
        
        async with async_session_factory() as session:
            await setup_demo_data(session)

        # RabbitMQ
        logger.info(f"Checking RabbitMQ connection at {settings.RABBITMQ_HOST}...")
        try:
            params = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST, 
                heartbeat=600,
                connection_attempts=3,
                retry_delay=2
            )
            connection = pika.BlockingConnection(params)
            connection.close()
            logger.info("RabbitMQ connection successful")
        except Exception as rabbit_err:
            logger.warning(f"RabbitMQ is not ready yet: {rabbit_err}. Continuing startup...")

        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Critical startup failed: {str(e)}")
        raise e

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutting down...")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        'app.api:app',
        host='0.0.0.0',
        port=8080,
        reload=True
    )