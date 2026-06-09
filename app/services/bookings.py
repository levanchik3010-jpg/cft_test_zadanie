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
    db: AsyncSession, data: BookingCreate, user: User
) -> Booking:
    # Проверяем что комната существует
    res = await db.execute(select(Room).where(Room.id == data.room_id))
    room = res.scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")

    # Проверяем что слот принадлежит этой комнате
    res = await db.execute(
        select(TimeSlot).where(
            TimeSlot.id == data.time_slot_id,
            TimeSlot.room_id == data.room_id,
        )
    )
    slot = res.scalar_one_or_none()
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Временной слот не найден для данной комнаты",
        )

    # Проверяем что слот не занят на эту дату
    res = await db.execute(
        select(Booking).where(
            and_(
                Booking.room_id == data.room_id,
                Booking.time_slot_id == data.time_slot_id,
                Booking.date == data.date,
                Booking.status == BookingStatus.active,
            )
        )
    )
    if res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот слот уже забронирован на выбранную дату",
        )

    booking = Booking(
        user_id=user.id,
        room_id=data.room_id,
        time_slot_id=data.time_slot_id,
        date=data.date,
        status=BookingStatus.active,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    # Загружаем связанные данные для ответа
    res = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room),
            selectinload(Booking.user),
        )
        .where(Booking.id == booking.id)
    )
    return res.scalar_one()


# Мои бронирования — только текущего пользователя
async def get_my_bookings(db: AsyncSession, user: User) -> list[Booking]:
    res = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room),
        )
        .where(Booking.user_id == user.id)
        .order_by(Booking.date.desc(), Booking.id.desc())
    )
    return res.scalars().all()


# Все бронирования — для администратора
async def get_all_bookings(db: AsyncSession) -> list[Booking]:
    res = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.time_slot),
            selectinload(Booking.room).selectinload(Room.time_slots),
            selectinload(Booking.user),
        )
        .order_by(Booking.date.desc(), Booking.id.desc())
    )
    return res.scalars().all()


async def cancel_booking(
    db: AsyncSession, booking_id: int, user: User
) -> Booking:
    res = await db.execute(
        select(Booking)
        .options(selectinload(Booking.time_slot), selectinload(Booking.room))
        .where(Booking.id == booking_id)
    )
    booking = res.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")

    # Сотрудник может отменить только своё бронирование
    if user.role != UserRole.admin and booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно отменять только свои бронирования",
        )

    if booking.status == BookingStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Бронирование уже отменено",
        )

    booking.status = BookingStatus.cancelled
    await db.commit()
    await db.refresh(booking)
    return booking
