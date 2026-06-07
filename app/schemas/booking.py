from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel
from app.models.booking import BookingStatus
from app.schemas.room import TimeSlotOut, RoomOut
from app.schemas.user import UserOut


class BookingCreate(BaseModel):
    room_id: int
    time_slot_id: int
    date: date


class BookingOut(BaseModel):
    id: int
    room_id: int
    time_slot_id: int
    date: date
    status: BookingStatus
    created_at: datetime
    user_id: int
    time_slot: TimeSlotOut

    model_config = {"from_attributes": True}


class BookingOutDetailed(BookingOut):
    user: UserOut
    room: RoomOut
