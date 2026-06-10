import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_list_rooms(client: AsyncClient, employee_user, room_with_slots):
    resp = await client.get("/api/v1/rooms", headers=auth_headers(employee_user))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Room"
    assert len(data[0]["time_slots"]) == 3


@pytest.mark.asyncio
async def test_get_room(client: AsyncClient, employee_user, room_with_slots):
    resp = await client.get(f"/api/v1/rooms/{room_with_slots.id}", headers=auth_headers(employee_user))
    assert resp.status_code == 200
    assert resp.json()["id"] == room_with_slots.id


@pytest.mark.asyncio
async def test_get_room_not_found(client: AsyncClient, employee_user):
    resp = await client.get("/api/v1/rooms/99999", headers=auth_headers(employee_user))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_room_availability_all_free(client: AsyncClient, employee_user, room_with_slots):
    resp = await client.get(
        f"/api/v1/rooms/{room_with_slots.id}/availability",
        params={"date": "2026-12-01"},
        headers=auth_headers(employee_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["available_slots"]) == 3
    assert len(data["booked_slots"]) == 0


@pytest.mark.asyncio
async def test_room_availability_after_booking(
    client: AsyncClient, employee_user, room_with_slots
):
    slot_id = room_with_slots.time_slots[0].id
    await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2026-12-01"},
        headers=auth_headers(employee_user),
    )

    resp = await client.get(
        f"/api/v1/rooms/{room_with_slots.id}/availability",
        params={"date": "2026-12-01"},
        headers=auth_headers(employee_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["available_slots"]) == 2
    assert len(data["booked_slots"]) == 1
