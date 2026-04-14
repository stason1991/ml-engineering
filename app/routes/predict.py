from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from schemas.predict import PredictionRequest
from services.crud import prediction_service
from services.crud.auth_service import get_current_user
from models.user import User

predict_router = APIRouter()

@predict_router.post("/")
async def predict(
    data: PredictionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Сквозной сценарий: проверка баланса -> предсказание -> списание -> история"""
    return await prediction_service.execute_prediction(
        user_id=current.user_id,
        model_id=data.model_id,
        session=session
    )
