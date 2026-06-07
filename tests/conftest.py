import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from datetime import time
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import app.db as db_module
from app.main import app
from app.db import Base, get_db
from app.models.user import User, UserRole
from app.models.room import Room, TimeSlot
from app.services.auth import get_password_hash, create_access_token

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Patch the global engine so the app uses the same database as tests
    db_module._engine = engine
    db_module._session_factory = async_sessionmaker(engine, expire_on_commit=False)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    db_module._engine = None
    db_module._session_factory = None


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    async with db_module._session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_engine):
    async def override_get_db():
        async with db_module._session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        username="testadmin",
        hashed_password=get_password_hash("adminpass"),
        full_name="Test Admin",
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee_user(db_session: AsyncSession) -> User:
    user = User(
        username="testemployee",
        hashed_password=get_password_hash("emppass"),
        full_name="Test Employee",
        role=UserRole.employee,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee_user2(db_session: AsyncSession) -> User:
    user = User(
        username="testemployee2",
        hashed_password=get_password_hash("emppass2"),
        full_name="Test Employee 2",
        role=UserRole.employee,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def room_with_slots(db_session: AsyncSession) -> Room:
    room = Room(name="Test Room", description="A test room", capacity=10)
    db_session.add(room)
    await db_session.flush()

    slots = [
        TimeSlot(room_id=room.id, label="09:00–11:00", start_time=time(9, 0), end_time=time(11, 0)),
        TimeSlot(room_id=room.id, label="11:00–13:00", start_time=time(11, 0), end_time=time(13, 0)),
        TimeSlot(room_id=room.id, label="13:00–15:00", start_time=time(13, 0), end_time=time(15, 0)),
    ]
    for slot in slots:
        db_session.add(slot)

    await db_session.commit()

    result = await db_session.execute(
        select(Room).options(selectinload(Room.time_slots)).where(Room.id == room.id)
    )
    return result.scalar_one()


def make_token(user: User) -> str:
    return create_access_token({"sub": user.username, "role": user.role})


def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {make_token(user)}"}
