"""Create tables and seed initial data."""
import asyncio
from datetime import time

from sqlalchemy import select

import app.models  # noqa: F401 – ensure all models are registered
from app.db import Base, _get_engine, _get_session_factory
from app.models import Room, TimeSlot, User
from app.models.user import UserRole
from app.services.auth import get_password_hash


ROOMS_DATA = [
    {
        "name": "Переговорная «Альфа»",
        "description": "Небольшая переговорная на 6 человек",
        "capacity": 6,
        "slots": [
            ("09:00–11:00", time(9, 0), time(11, 0)),
            ("11:00–13:00", time(11, 0), time(13, 0)),
            ("13:00–15:00", time(13, 0), time(15, 0)),
            ("15:00–17:00", time(15, 0), time(17, 0)),
            ("17:00–19:00", time(17, 0), time(19, 0)),
        ],
    },
    {
        "name": "Переговорная «Бета»",
        "description": "Просторный зал для презентаций на 20 человек",
        "capacity": 20,
        "slots": [
            ("09:00–12:00", time(9, 0), time(12, 0)),
            ("12:00–15:00", time(12, 0), time(15, 0)),
            ("15:00–18:00", time(15, 0), time(18, 0)),
        ],
    },
    {
        "name": "Переговорная «Гамма»",
        "description": "Кабинет для конфиденциальных переговоров на 4 человека",
        "capacity": 4,
        "slots": [
            ("10:00–12:00", time(10, 0), time(12, 0)),
            ("13:00–16:00", time(13, 0), time(16, 0)),
            ("16:00–19:00", time(16, 0), time(19, 0)),
        ],
    },
]

DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "full_name": "Администратор", "role": UserRole.admin},
    {"username": "employee1", "password": "pass123", "full_name": "Иван Иванов", "role": UserRole.employee},
    {"username": "employee2", "password": "pass123", "full_name": "Мария Петрова", "role": UserRole.employee},
]


async def create_tables():
    async with _get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    async with _get_session_factory()() as db:
        for user_data in DEFAULT_USERS:
            result = await db.execute(select(User).where(User.username == user_data["username"]))
            if result.scalar_one_or_none() is None:
                user = User(
                    username=user_data["username"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                )
                db.add(user)

        for room_data in ROOMS_DATA:
            result = await db.execute(select(Room).where(Room.name == room_data["name"]))
            if result.scalar_one_or_none() is None:
                room = Room(
                    name=room_data["name"],
                    description=room_data["description"],
                    capacity=room_data["capacity"],
                )
                db.add(room)
                await db.flush()

                for label, start, end in room_data["slots"]:
                    slot = TimeSlot(
                        room_id=room.id,
                        label=label,
                        start_time=start,
                        end_time=end,
                    )
                    db.add(slot)

        await db.commit()


async def init():
    await create_tables()
    await seed_data()


if __name__ == "__main__":
    asyncio.run(init())
