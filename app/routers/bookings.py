from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut, BookingOutDetailed
from app.services import bookings as booking_service

router = APIRouter(prefix="/bookings", tags=["бронирования"])


# Создать бронирование
@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED, summary="Создать бронирование")
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await booking_service.create_booking(db, data, user)


# Мои бронирования
@router.get("/my", response_model=list[BookingOut], summary="Мои бронирования")
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await booking_service.get_my_bookings(db, user)


# Все бронирования — только для администратора
@router.get("", response_model=list[BookingOutDetailed], summary="Все бронирования (только админ)")
async def all_bookings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await booking_service.get_all_bookings(db)


# Отменить бронирование
@router.delete("/{booking_id}", response_model=BookingOut, summary="Отменить бронирование")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await booking_service.cancel_booking(db, booking_id, user)
