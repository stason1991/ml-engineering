from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager # Добавлено для удобства воркера
from app.database.config import get_settings
from app.models.base import Base
# Импорты моделей (убедитесь, что пути корректны относительно этого файла)
from app.models.user import User
from app.models.profile import BankEmployeeProfile
from app.models.wallet import Wallet
from app.models.transaction import Transaction, DebitTransaction, CreditTransaction
from app.models.history import PredictionHistory
from app.models.ml_model import MLModel, EuclideanKMeansModel
from app.models.centroid import Centroid

settings = get_settings()

# 1. Создаём асинхронный движок
engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg, 
    echo=False, # Сменил на False для воркера, чтобы логи не забивались SQL-запросами
    pool_size=5, 
    max_overflow=10
)

# 2. Асинхронная фабрика сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Контекстный менеджер для воркера (Чтобы сессия всегда закрывалась)
@asynccontextmanager
async def get_worker_session():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# 4. Инициализация таблиц
async def init_db():
    """Создает таблицы, если они не существуют"""
    async with engine.begin() as conn:
        # В режиме разработки можно раскомментировать drop_all для сброса
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# 5. Генератор для FastAPI (остается для ваших REST-эндпоинтов)
async def get_session():
    async with async_session_factory() as session:
        yield session