from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from schemas.predict import PredictionRequest
from services.crud import prediction_service

predict_router = APIRouter()

@predict_router.post("/")
async def get_prediction(
    data: PredictionRequest,
    session: AsyncSession = Depends(get_session)
):
    """Сквозной сценарий: проверка баланса -> предсказание -> списание -> история"""
    return await prediction_service.execute_prediction(
        user_id=data.user_id,
        model_id=data.model_id,
        session=session
    )
