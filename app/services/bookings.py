from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking, BookingStatus
from app.models.room import Room, TimeSlot
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate


async def create_booking(
    db: AsyncSession, data: BookingCreate, current_user: User
) -> Booking:
    room_result = await db.execute(select(Room).where(Room.id == data.room_id))
    room = room_result.scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    slot_result = await db.execute(
        select(TimeSlot).where(
            TimeSlot.id == data.time_slot_id,
            TimeSlot.room_id == data.room_id,
        )
    )
    slot = slot_result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found for this room",
        )

    conflict_result = await db.execute(
        select(Booking).where(
            and_(
                Booking.room_id == data.room_id,
                Booking.time_slot_id == data.time_slot_id,
                Booking.date == data.date,
                Booking.status == BookingStatus.active,
            )
        )
    )
    if conflict_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This slot is already booked for the selected date",
        )

    booking = Booking(
        user_id=current_user.id,
        room_id=data.room_id,
        time_slot_id=data.time_slot_id,
        date=data.date,
        status=BookingStatus.active,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room),
            selectinload(Booking.user),
        )
        .where(Booking.id == booking.id)
    )
    return result.scalar_one()


async def get_my_bookings(db: AsyncSession, current_user: User) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room),
        )
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.date.desc(), Booking.id.desc())
    )
    return result.scalars().all()


async def get_all_bookings(db: AsyncSession) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room),
            selectinload(Booking.user),
        )
        .order_by(Booking.date.desc(), Booking.id.desc())
    )
    return result.scalars().all()


async def cancel_booking(
    db: AsyncSession, booking_id: int, current_user: User
) -> Booking:
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.time_slot), selectinload(Booking.room))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if current_user.role != UserRole.admin and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings",
        )

    if booking.status == BookingStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is already cancelled",
        )

    booking.status = BookingStatus.cancelled
    await db.commit()
    await db.refresh(booking)
    return booking
