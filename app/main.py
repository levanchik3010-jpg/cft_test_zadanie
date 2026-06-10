from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.init_db import init as init_database
from app.routers import auth, rooms, bookings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(
    title="Сервис бронирования переговорных комнат",
    description="API для бронированием переговорных комнат в коворкинге",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")


@app.get("/health", tags=["проверка"], summary="Проверка работоспособности")
async def health():
    return {"status": "ok"}
