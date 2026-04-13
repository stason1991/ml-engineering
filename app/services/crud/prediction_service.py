from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException, status
from services.crud import wallet_service, profile_service, history_service, user_service, ml_model_service
from models.history import PredictionHistory

COST_PER_PREDICTION = 1000.0

async def execute_prediction(user_id: UUID, model_id: int, session: AsyncSession):
    # Авторизация
    user = await user_service.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Пользователь не авторизован или не найден"
        )

    # Проверяем модель
    ml_model = await session.get(ml_model_service.MLModel, model_id)
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"ML-модель с ID {model_id} не существует"
        )

    # Проверяем баланс
    wallet = await wallet_service.get_wallet_by_user_id(user_id, session)
    if not wallet or wallet.balance < COST_PER_PREDICTION:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail="Недостаточно средств для выполнения предсказания"
        )

    # Проверяем данные профиля
    profile = await profile_service.get_profile_by_user_id(user_id, session)
    if not profile or not profile.attributes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Данные профиля некорректны или отсутствуют"
        )

    # Работа модели
    role = profile.attributes.get('role', 'employee')
    prediction_result = f"Модель '{ml_model.name}' определила кластер для роли: {role}"

    # Транзакция
    new_balance = wallet.balance - COST_PER_PREDICTION
    await wallet_service.update_wallet_balance(user_id, new_balance, session)

    # Сохраняем в историю
    history_entry = PredictionHistory(
        user_id=user_id,
        result=prediction_result,
        data_snapshot=[float(x) for x in range(5)] # Пример вектора данных
    )
    await history_service.add_history_entry(history_entry, session)

    return {
        "status": "success",
        "model_used": ml_model.name,
        "prediction": prediction_result,
        "spent": COST_PER_PREDICTION,
        "balance_after": new_balance
    }
