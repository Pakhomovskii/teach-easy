import logging
from aiohttp import web
from pydantic import ValidationError
from app.models import CourseInput, ClassInput, Teacher, Icon, Course, Class
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db import async_session_maker


async def get_courses(request):
    async with async_session_maker() as session:
        courses = await session.scalars(
            select(Course).options(joinedload(Course.icon))
        )
        return web.json_response(
            [course.to_dict() for course in courses.all()]
        )


async def create_course(request):
    try:
        data = CourseInput(**await request.json())

        async with async_session_maker() as session:
            teacher = await session.get(Teacher, data.teacher_id)
            if not teacher:
                raise web.HTTPNotFound(reason="Teacher not found")

            icon = None
            if data.icon_id:
                icon = await session.get(Icon, data.icon_id)
                if not icon:
                    raise web.HTTPBadRequest(reason="Icon with given ID does not exist")

            new_course = Course(
                title=data.title, description=data.description, teacher=teacher, icon=icon
            )
            session.add(new_course)
            await session.commit()

            return web.json_response(new_course.to_dict(), status=201)

    except ValidationError as e:
        logging.error(f"ValidationError: {e.errors()}")
        return web.json_response({"error": e.errors()}, status=400)

    except AttributeError:
        return web.json_response({"error": "icon_id is required"}, status=400)

    except Exception as e:
        logging.exception("Unexpected error")
        return web.json_response({"error": "Internal server error"}, status=500)


async def create_class(request):
    try:
        data = ClassInput(**await request.json())
        async with async_session_maker() as session:
            new_class = Class(**data.dict())
            session.add(new_class)
            await session.commit()
            return web.json_response(new_class.to_dict(), status=201)
    except ValidationError as e:
        return web.json_response({"error": e.errors()}, status=400)


async def get_icons(request):
    async with async_session_maker() as session:
        icons = await session.scalars(select(Icon))
        return web.json_response([icon.to_dict() for icon in icons.all()])


async def get_courses_by_teacher(request):
    teacher_id = int(request.match_info['teacher_id'])
    async with async_session_maker() as session:
        courses = await session.scalars(select(Course).where(Course.teacher_id == teacher_id))
        return web.json_response([course.to_dict() for course in courses.all()])
