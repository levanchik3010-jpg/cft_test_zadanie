from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking, BookingStatus
from app.models.room import Room, TimeSlot


async def get_all_rooms(db: AsyncSession) -> list[Room]:
    result = await db.execute(
        select(Room).options(selectinload(Room.time_slots)).order_by(Room.id)
    )
    return result.scalars().all()


async def get_room(db: AsyncSession, room_id: int) -> Room | None:
    result = await db.execute(
        select(Room)
        .options(selectinload(Room.time_slots))
        .where(Room.id == room_id)
    )
    return result.scalar_one_or_none()


async def get_room_availability(
    db: AsyncSession, room_id: int, check_date: date
) -> dict:
    room = await get_room(db, room_id)
    if room is None:
        return None

    booked_result = await db.execute(
        select(Booking.time_slot_id)
        .where(
            Booking.room_id == room_id,
            Booking.date == check_date,
            Booking.status == BookingStatus.active,
        )
    )
    booked_slot_ids = set(booked_result.scalars().all())

    available = [s for s in room.time_slots if s.id not in booked_slot_ids]
    booked = [s for s in room.time_slots if s.id in booked_slot_ids]

    return {"room": room, "available_slots": available, "booked_slots": booked}
