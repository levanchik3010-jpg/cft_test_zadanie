from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut, BookingOutDetailed
from app.services import bookings as booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.create_booking(db, data, current_user)


@router.get("/my", response_model=list[BookingOut])
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.get_my_bookings(db, current_user)


@router.get("", response_model=list[BookingOutDetailed])
async def all_bookings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await booking_service.get_all_bookings(db)


@router.delete("/{booking_id}", response_model=BookingOut)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.cancel_booking(db, booking_id, current_user)
