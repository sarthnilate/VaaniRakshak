import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.database import init_db
from backend.db.redis import session_manager


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Initializes in-memory database and Redis fallback before test execution."""
    await init_db()
    await session_manager.initialize()


@pytest_asyncio.fixture
async def async_client():
    """Provides async HTTP client for FastAPI integration testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
