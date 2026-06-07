from datetime import time
from pydantic import BaseModel


class TimeSlotOut(BaseModel):
    id: int
    label: str
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class RoomOut(BaseModel):
    id: int
    name: str
    description: str | None
    capacity: int | None
    time_slots: list[TimeSlotOut] = []

    model_config = {"from_attributes": True}


class RoomAvailability(BaseModel):
    date: str
    room: RoomOut
    available_slots: list[TimeSlotOut]
    booked_slots: list[TimeSlotOut]
