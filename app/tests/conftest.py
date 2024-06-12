import pytest
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.routes import create_course, get_courses
from templates.const import TEST_DATABASE_URL


@pytest.fixture
async def init_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

    async with engine.begin() as conn:
        pass

    yield TestingSessionLocal

    await engine.dispose()


@pytest.fixture
async def client(aiohttp_client, init_db):
    app = web.Application()
    app["db_session"] = init_db

    app.router.add_post("/courses/", create_course)
    app.router.add_get("/courses/", get_courses)

    return await aiohttp_client(app)
