from sqlalchemy import Column, Integer, String, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    capacity = Column(Integer, nullable=True)

    time_slots = relationship("TimeSlot", back_populates="room", lazy="select")
    bookings = relationship("Booking", back_populates="room", lazy="select")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    __table_args__ = (UniqueConstraint("room_id", "label", name="uq_room_slot_label"),)

    room = relationship("Room", back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot", lazy="select")
