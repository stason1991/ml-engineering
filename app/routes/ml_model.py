from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from models.ml_model import MLModel
from services.crud import ml_model_service as service
from database.database import get_session
from schemas.ml_model import MLModelCreate, MLModelResponse

ml_model_router = APIRouter()

@ml_model_router.get("/", response_model=List[MLModelResponse])
async def read_all_models(
    session: AsyncSession = Depends(get_session)
):
    """Получить список всех доступных ML-моделей"""
    return await service.get_all_models(session)

@ml_model_router.get("/{name}", response_model=MLModelResponse)
async def read_model_by_name(
    name: str, 
    session: AsyncSession = Depends(get_session)
):
    """Найти модель по её уникальному имени"""
    model = await service.get_model_by_name(name, session)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Модель с именем {name} не найдена"
        )
    return model

@ml_model_router.post("/", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def create_new_model(
    data: MLModelCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Регистрация новой ML-модели в системе"""
    existing = await service.get_model_by_name(data.name, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Модель с таким именем уже существует"
        )
    
    return await service.create_ml_model(
        name=data.name, 
        description=data.description, 
        session=session
    )

@ml_model_router.post("/setup-demo", status_code=status.HTTP_200_OK)
async def run_demo_setup(
    session: AsyncSession = Depends(get_session)
):
    """
    Запустить инициализацию демо-данных
    """
    try:
        await service.init_base_models(session)
        return {"status": "success", "message": "Демо-данные успешно инициализированы"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка при инициализации: {str(e)}"
        )
