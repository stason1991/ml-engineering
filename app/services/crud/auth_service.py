import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
from app.database.database import get_session

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
    if user.password_hash != f"hash_{password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )

    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Получение текущего пользователя по JWT токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw: str = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception

        user_id = UUID(user_id_raw) # Преобразовываем тип в UUID
    except (JWTError, ValueError):
        raise credentials_exception
        
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден в базе")
        
    return user
