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


async def startup(app):
    app['db_session'] = sessionmaker(
        create_async_engine(DATABASE_URL, echo=True),
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with app['db_session']().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for model in (Teacher, Class, Subject, Course, Icon):
        add_to_dict_method(model)


async def cleanup(app):
    await app['db_session']().bind.dispose()


app.on_startup.append(startup)
app.on_cleanup.append(cleanup)


async def main():
    logging.basicConfig(level=logging.INFO)
    await web._run_app(app, host='localhost', port=8080)


if __name__ == '__main__':
    asyncio.run(main())
