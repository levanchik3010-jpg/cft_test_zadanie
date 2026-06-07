import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient, employee_user, room_with_slots):
    slot_id = room_with_slots.time_slots[0].id
    resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-15"},
        headers=auth_headers(employee_user),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "active"
    assert data["user_id"] == employee_user.id
    assert data["room_id"] == room_with_slots.id


@pytest.mark.asyncio
async def test_create_booking_conflict(client: AsyncClient, employee_user, employee_user2, room_with_slots):
    slot_id = room_with_slots.time_slots[0].id
    payload = {"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-16"}

    resp1 = await client.post("/api/v1/bookings", json=payload, headers=auth_headers(employee_user))
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/bookings", json=payload, headers=auth_headers(employee_user2))
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_booking_wrong_slot(client: AsyncClient, employee_user, room_with_slots):
    resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": 99999, "date": "2025-12-15"},
        headers=auth_headers(employee_user),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_my_bookings(client: AsyncClient, employee_user, employee_user2, room_with_slots):
    slot_id = room_with_slots.time_slots[0].id
    await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-20"},
        headers=auth_headers(employee_user),
    )

    resp = await client.get("/api/v1/bookings/my", headers=auth_headers(employee_user))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["user_id"] == employee_user.id

    resp2 = await client.get("/api/v1/bookings/my", headers=auth_headers(employee_user2))
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


@pytest.mark.asyncio
async def test_all_bookings_admin_only(client: AsyncClient, employee_user, admin_user, room_with_slots):
    resp_emp = await client.get("/api/v1/bookings", headers=auth_headers(employee_user))
    assert resp_emp.status_code == 403

    resp_admin = await client.get("/api/v1/bookings", headers=auth_headers(admin_user))
    assert resp_admin.status_code == 200


@pytest.mark.asyncio
async def test_cancel_own_booking(client: AsyncClient, employee_user, room_with_slots):
    slot_id = room_with_slots.time_slots[1].id
    create_resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-22"},
        headers=auth_headers(employee_user),
    )
    booking_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(employee_user))
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_others_booking_forbidden(
    client: AsyncClient, employee_user, employee_user2, room_with_slots
):
    slot_id = room_with_slots.time_slots[2].id
    create_resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-23"},
        headers=auth_headers(employee_user),
    )
    booking_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(employee_user2))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_cancel_any_booking(
    client: AsyncClient, admin_user, employee_user, room_with_slots
):
    slot_id = room_with_slots.time_slots[0].id
    create_resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-24"},
        headers=auth_headers(employee_user),
    )
    booking_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_already_cancelled(client: AsyncClient, employee_user, room_with_slots):
    slot_id = room_with_slots.time_slots[1].id
    create_resp = await client.post(
        "/api/v1/bookings",
        json={"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-25"},
        headers=auth_headers(employee_user),
    )
    booking_id = create_resp.json()["id"]

    await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(employee_user))
    resp = await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(employee_user))
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_cancelled_slot_becomes_available_again(
    client: AsyncClient, employee_user, employee_user2, room_with_slots
):
    slot_id = room_with_slots.time_slots[0].id
    payload = {"room_id": room_with_slots.id, "time_slot_id": slot_id, "date": "2025-12-26"}

    create_resp = await client.post("/api/v1/bookings", json=payload, headers=auth_headers(employee_user))
    booking_id = create_resp.json()["id"]

    await client.delete(f"/api/v1/bookings/{booking_id}", headers=auth_headers(employee_user))

    resp2 = await client.post("/api/v1/bookings", json=payload, headers=auth_headers(employee_user2))
    assert resp2.status_code == 201
