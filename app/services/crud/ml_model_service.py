from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ml_model import MLModel, EuclideanKMeansModel
from app.models.user import User
from app.models.wallet import Wallet
from app.models.profile import BankEmployeeProfile
from app.models.history import PredictionHistory
from app.services.crud.auth_service import get_password_hash

async def get_model_by_name(name: str, session: AsyncSession) -> Optional[MLModel]:
    """Найти модель по имени"""
    result = await session.execute(select(MLModel).where(MLModel.name == name))
    return result.scalars().first()

async def get_all_models(session: AsyncSession) -> List[MLModel]:
    """Получить список всех ML-моделей"""
    result = await session.execute(select(MLModel))
    return list(result.scalars().all())

async def create_ml_model(name: str, description: str, session: AsyncSession) -> MLModel:
    """Создать новую ML-модель"""
    new_model = EuclideanKMeansModel(name=name, description=description)
    session.add(new_model)
    await session.commit()
    await session.refresh(new_model)
    return new_model

async def setup_demo_data(session: AsyncSession):
    """
    Сценарий полной инициализации БД:
    1. Базовые ML-модели
    2. Демо-пользователь
    3. Кошелек с балансом
    4. Профиль сотрудника
    5. Запись в истории транзакций
    """
    print("\n[Начало инициализации демо-данных]")

    # 1. Инициализация базовой модели
    existing_ml = await get_model_by_name("Career Path Pro", session)
    if not existing_ml:
        print("Инициализация: Создание базовой модели Career Path Pro...")
        await create_ml_model(
            name="Career Path Pro",
            description="Стандартная модель кластеризации сотрудников по KPI",
            session=session
        )
        print("Базовая модель 'Career Path Pro' создана!")

    # 2. Проверяем и создаём демо-пользователя
    res = await session.execute(select(User).where(User.login == "user_demo"))
    demo_user = res.scalars().first()

    if not demo_user:
        # Создаём пользователя
        demo_user = User(login="user_demo", password_hash=get_password_hash("demo_password_123"))
        session.add(demo_user)
        await session.commit()
        await session.refresh(demo_user)

        # Создаём кошелёк
        demo_wallet = Wallet(user_id=demo_user.id, balance=10000.0)
        session.add(demo_wallet)
        await session.commit()
        await session.refresh(demo_wallet)

        # Создаём профиль
        demo_profile = BankEmployeeProfile(
            user_id=demo_user.id,
            attributes={"role": "manager", "department": "Retail block"}
        )
        session.add(demo_profile)
        await session.commit()

        # Создаём запись в истории
        demo_history = PredictionHistory(
            user_id=demo_user.id,
            result="Initial seed deposit",
            data_snapshot=[10000.0],
            timestamp=datetime.utcnow()
        )
        session.add(demo_history)
        await session.commit()

        print(f"Демо-user '{demo_user.login}' создан. Пароль: demo_password_123")


    print("[Инициализация завершена]\n")

async def init_base_models(session: AsyncSession):
    """Обертка для вызова из main.py"""
    await setup_demo_data(session)