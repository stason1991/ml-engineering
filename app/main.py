import sys
import asyncio
from sqlalchemy import select

from database import init_db, async_session_factory
from models import User, Wallet, MLModel, Transaction
from services.crud.ml_model_service import setup_demo_data
from services.crud.transaction_service import execute_transaction, get_all_transactions

async def main():
    print("Ожидание запуска PostgreSQL......")
    await asyncio.sleep(5)

    # Создание таблиц
    print("Синхронизация структуры базы данных...")
    await init_db()
    print("База данных создана")

    # Запуск инициализации
    async with async_session_factory() as session:
        print("\nИнициализация базовых данных и ML-моделей...")
        await setup_demo_data(session)

    # Тестирование транзакции
    async with async_session_factory() as session:
        # Получаем созданного демо-пользователя для теста
        result = await session.execute(select(User).where(User.login == "user_demo"))
        user = result.scalars().first()
        
        if user:
            # Получаем кошелёк
            res_w = await session.execute(select(Wallet).where(Wallet.user_id == user.id))
            wallet = res_w.scalars().first()

            if wallet:
                print(f"\n--- Тестирование транзакций для {user.login} ---")
                print(f"Баланс до операций: {wallet.balance}")

                # Тест: Пополнение (Credit)
                await execute_transaction(wallet.id, 20000.0, "credit", session)
                await session.refresh(wallet)
                print(f"Баланс после пополнения (+20000.0): {wallet.balance}")

                # Тест: Списание за прогноз (Debit)
                await execute_transaction(wallet.id, 7899, "debit", session)
                await session.refresh(wallet)
                print(f"Баланс после списания за прогноз (-7899): {wallet.balance}")

    # Вывод всех данных из БД
    print("\n" + "="*40)
    print("ИТОГОВЫЙ СПИСОК ПОЛЬЗОВАТЕЛЕЙ И ТРАНЗАКЦИЙ:")
    print("="*40)

    async with async_session_factory() as session:
        # Список пользователей
        res_users = await session.execute(select(User))
        users = res_users.scalars().all()
        for u in users:
            print(f"User: {u.login} (ID: {str(u.id)[:8]}...)")

        # Список всех транзакций
        txs = await get_all_transactions(session)
        print(f"\nВсего транзакций в истории: {len(txs)}")
        for tx in txs[:5]: # Вывод последних 5
            print(f" - [{tx.timestamp.strftime('%H:%M:%S')}] {tx.type}: {tx.amount}")

    print("\nПроверка завершена успешно!", flush=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПроцесс прерван пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка при запуске: {e}")
        sys.exit(1)