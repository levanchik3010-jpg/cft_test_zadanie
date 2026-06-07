from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking, BookingStatus
from app.models.room import Room, TimeSlot


# Получить все комнаты вместе со слотами
async def get_all_rooms(db: AsyncSession) -> list[Room]:
    res = await db.execute(
        select(Room).options(selectinload(Room.time_slots)).order_by(Room.id)
    )
    return res.scalars().all()


# Получить одну комнату по id
async def get_room(db: AsyncSession, room_id: int) -> Room | None:
    res = await db.execute(
        select(Room)
        .options(selectinload(Room.time_slots))
        .where(Room.id == room_id)
    )
    return res.scalar_one_or_none()


# Проверить доступность слотов комнаты на дату
async def get_room_availability(
    db: AsyncSession, room_id: int, target_date: date
) -> dict:
    room = await get_room(db, room_id)
    if room is None:
        return None

    # Смотрим какие слоты уже заняты на эту дату
    res = await db.execute(
        select(Booking.time_slot_id)
        .where(
            Booking.room_id == room_id,
            Booking.date == target_date,
            Booking.status == BookingStatus.active,
        )
    )
    busy_ids = set(res.scalars().all())

    free_slots = [s for s in room.time_slots if s.id not in busy_ids]
    busy_slots = [s for s in room.time_slots if s.id in busy_ids]

    return {"room": room, "available_slots": free_slots, "booked_slots": busy_slots}
