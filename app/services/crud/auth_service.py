from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from fastapi import HTTPException, status

async def authenticate_user(login: str, password: str, session: AsyncSession):
    # Ищем пользователя по логину
    result = await session.execute(select(User).where(User.login == login))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    # Проверка пароля
    if user.password_hash != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )

    return user
