from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException, status
from app.services.crud import wallet_service, profile_service, history_service, user_service, ml_model_service
from app.services.crud.transaction_service import execute_transaction # Импортируем сервис транзакций
from app.models.history import PredictionHistory

COST_PER_PREDICTION = 100.0

async def execute_prediction(user_id: UUID, model_id: int, session: AsyncSession):
    # 1. Проверка пользователя
    user = await user_service.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Пользователь не авторизован или не найден"
        )

    # 2. Проверяем наличие модели
    ml_model = await session.get(ml_model_service.MLModel, model_id)
    if not ml_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"ML-модель с ID {model_id} не существует"
        )

    # 3. Проверяем кошелек и баланс
    wallet = await wallet_service.get_wallet_by_user_id(user_id, session)
    if not wallet or wallet.balance < COST_PER_PREDICTION:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail=f"Недостаточно средств. Нужно: {COST_PER_PREDICTION}, ваш баланс: {wallet.balance if wallet else 0}"
        )

    # 4. Проверяем данные профиля для предсказания
    profile = await profile_service.get_profile_by_user_id(user_id, session)
    if not profile or not profile.attributes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Данные профиля отсутствуют. Заполните профиль перед анализом."
        )

    # 5. Выполняем финансовую операцию (Списание)
    # Обновление и запись в историю транзакций
    try:
        await execute_transaction(
            wallet_id=user_id,
            amount=COST_PER_PREDICTION,
            tx_type="debit",
            session=session
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка списания средств: {str(e)}"
        )

    # 6. Логика работы ML-модели
    role = profile.attributes.get('role', 'employee')
    prediction_result = f"Модель '{ml_model.name}' определила кластер для роли: {role}"

    # 7. Сохранение результата в историю предсказаний
    history_entry = PredictionHistory(
        user_id=user_id,
        result=prediction_result,
        data_snapshot=profile.attributes
    )
    await history_service.add_history_entry(history_entry, session)

    # Обновляем данные кошелька в текущей сессии, чтобы вернуть верный баланс
    await session.refresh(wallet)

    return {
        "status": "success",
        "model_used": ml_model.name,
        "prediction": prediction_result,
        "spent": COST_PER_PREDICTION,
        "balance_after": wallet.balance
    }