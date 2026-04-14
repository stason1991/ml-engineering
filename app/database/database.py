from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings
from models.base import Base
from models.user import User
from models.profile import BankEmployeeProfile
from models.wallet import Wallet
from models.transaction import Transaction, DebitTransaction, CreditTransaction
from models.history import PredictionHistory
from models.ml_model import MLModel, EuclideanKMeansModel
from models.centroid import Centroid

settings = get_settings()

#Создаём асинхронный движок (используем URL с asyncpg):
engine = create_async_engine(
  url=settings.DATABASE_URL_asyncpg, 
  echo=True, 
  pool_size=5, 
  max_overflow=10
)

#Асинхронная фабрика сессий:
async_session_factory = async_sessionmaker(
  bind=engine,
  class_=AsyncSession,
  expire_on_commit=False
)
        
async def init_db():
  """Инициализация таблиц"""
  async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)

async def get_session():
  async with async_session_factory() as session:
    yield session