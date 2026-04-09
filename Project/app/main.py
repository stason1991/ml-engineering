import sys
import os
import asyncio
from sqlalchemy.orm import joinedload
from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from uuid import uuid4
from database import init_db, engine, async_session_factory
from models import User, Wallet, BankEmployeeProfile
from services.crud import (
  create_user, 
  get_all_users, 
  create_wallet, 
  create_profile,
  init_base_models,
  execute_transaction
)

async def main():
  print("Ожидание запуска PostgreSQL......")
  await asyncio.sleep(5)
  # Cоздание таблиц
  print("Создание базы данных")
  await init_db()
  print("База данных успешно создана")

  #Инициализируем базовые ML-модели
  async with async_session_factory() as session:
    print("\nСоздание базовых ML-моделей")
    await init_base_models(session)
  

  # Создаем тестовых пользователей
  async with async_session_factory() as session:
  # Подготовка данных
    user1 = User(login="ivan_drago", password_hash="hash123")
    user2 = User(login="rayan_gosling", password_hash="hash456")

    print("Создание пользователей...")
    await create_user(user1, session)
    await create_user(user2, session)
    print(f"Пользователи созданы: {user1.login}, {user2.login}")

   # Создаем кошельки и пустые профили
    w1 = await create_wallet(Wallet(user_id=user1.id, balance=100.0), session)
    await create_profile(BankEmployeeProfile(user_id=user1.id, attributes={"kpi": 0.8}), session)
        
    w2 = await create_wallet(Wallet(user_id=user2.id, balance=50.0), session)
    print("Кошельки и профили инициализированы")

    #Тестирование бизнес-логики транзакций (Пополнение и Списание)
    print("\nТестирование транзакций")
        # Пополнение
    print(f"Баланс {user1.login} до пополнения: {w1.balance}")
    await execute_transaction(w1.id, 500.0, "credit", session)
    print(f"Баланс {user1.login} после пополнения (+500): {w1.balance}")

        # Списание за предсказание
    await execute_transaction(w1.id, 50.0, "debit", session)
    print(f"Баланс {user1.login} после списания за прогноз (-50): {w1.balance}")

        # Получение и вывод данных
    print("\nСписок пользователей из БД:")
    users = await get_all_users(session)
    for user in users:
      print(f"ID: {user.id} | Login: {user.login}")

  print("\nПроверка завершена успешно!", flush=True)


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("Процесс прерван пользователем")
  except Exception as e:
    print(f"Произошла ошибка при запуске: {e}")
