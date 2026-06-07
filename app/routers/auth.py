from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserOut
from app.services.auth import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


# Вход — возвращает JWT токен
@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == data.username))
    user = res.scalar_one_or_none()

    # Проверяем что пользователь существует и пароль верный
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=token)


# Регистрация нового пользователя
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем что логин не занят
    res = await db.execute(select(User).where(User.username == data.username))
    if res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такой логин уже занят",
        )

    user = User(
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
