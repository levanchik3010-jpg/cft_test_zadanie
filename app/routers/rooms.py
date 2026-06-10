from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.room import RoomAvailability, RoomOut
from app.services import rooms as room_service

router = APIRouter(prefix="/rooms", tags=["комнаты"])


# Список всех переговорных комнат
@router.get("", response_model=list[RoomOut], summary="Список всех комнат")
async def list_rooms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await room_service.get_all_rooms(db)


# Получить одну комнату по id
@router.get("/{room_id}", response_model=RoomOut, summary="Информация о комнате")
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    room = await room_service.get_room(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    return room


# Доступность слотов комнаты на конкретную дату
@router.get("/{room_id}/availability", response_model=RoomAvailability, summary="Свободные слоты на дату")
async def get_availability(
    room_id: int,
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    data = await room_service.get_room_availability(db, room_id, date)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    return RoomAvailability(
        date=str(date),
        room=data["room"],
        available_slots=data["available_slots"],
        booked_slots=data["booked_slots"],
    )
