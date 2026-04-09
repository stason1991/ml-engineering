from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.ml_model import MLModel, EuclideanKMeansModel

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

async def init_base_models(session: AsyncSession):
    """Идемпотентная инициализация базовых моделей"""
    existing = await get_model_by_name("Career Path Pro", session)
    if not existing:
        print("Инициализация: Создание базовой модели Career Path Pro...")
        await create_ml_model(
            name="Career Path Pro",
            description="Стандартная модель кластеризации сотрудников по KPI",
            session=session
        )