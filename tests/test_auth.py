import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "password": "secret123",
        "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == UserRole.employee


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, employee_user):
    resp = await client.post("/api/v1/auth/register", json={
        "username": employee_user.username,
        "password": "anypass",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, employee_user):
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testemployee",
        "password": "emppass",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, employee_user):
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testemployee",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={
        "username": "nobody",
        "password": "pass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/rooms")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_protected_endpoint_invalid_token(client: AsyncClient):
    resp = await client.get("/api/v1/rooms", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401
