from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_event_publisher
from app.infrastructure.db.models import Base
from app.infrastructure.db.session import get_db_session
from app.main import create_app
from tests.unit.fakes import FakeEventPublisher


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def fake_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest_asyncio.fixture
async def app(session_factory, fake_publisher):
    fastapi_app = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
    fastapi_app.dependency_overrides[get_event_publisher] = lambda: fake_publisher

    return fastapi_app


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
