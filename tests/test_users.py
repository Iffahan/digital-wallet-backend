import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from typing import Any, Dict, Optional
import pytest
import pytest_asyncio
import pathlib
import datetime

from digital_wallet import models, config, main, security

# Update settings for testing
SettingsTesting = config.Settings
SettingsTesting.model_config = config.SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)

# Fixture to create the app instance
@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app

# Fixture to create the HTTP client
@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

# Fixture to create a database session
@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncSession:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# Fixture to create a user
@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        password=password,
        email="test@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    await user.set_password(password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Test to create a user
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, session: models.AsyncSession) -> None:
    response = await client.post("/users/create", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
        "first_name": "New",
        "last_name": "User"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert data["last_login_date"] is None
