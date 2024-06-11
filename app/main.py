import asyncio
import logging
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from templates.const import DATABASE_URL
from models import Teacher, Class, Subject, Course, Icon
from routes import get_courses, create_course, create_class, get_icons, get_courses_by_teacher
from utils import add_to_dict_method


Base = declarative_base()


app = web.Application()
app.add_routes([
    web.get('/courses', get_courses),
    web.post('/courses', create_course),
    web.post('/classes', create_class),
    web.get('/icons', get_icons),
    web.get('/courses/teacher/{teacher_id}', get_courses_by_teacher),
])


async def main():
    """
        Asynchronous main function to set up and start the web application.

        This function performs the following operations:
        - Initializes the SQLAlchemy async engine with the database URL.
        - Creates a sessionmaker for asynchronous sessions with the database.
        - Creates all tables in the database if they do not already exist.
        - Adds a custom method to each model class for dictionary conversion.
        - Starts the aiohttp web application on localhost at port 8080.

        Globals:
        - engine: The SQLAlchemy async engine instance used for database connections.
        - async_session_maker: A sessionmaker instance configured for async sessions.
        """
    global engine
    global async_session_maker
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for model in (Teacher, Class, Subject, Course, Icon):
        add_to_dict_method(model)

    await web._run_app(app, host='localhost', port=8080)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
