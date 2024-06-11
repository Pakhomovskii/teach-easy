import asyncio
import logging

from aiohttp import web
from pydantic import BaseModel, Field, validator, ValidationError
from sqlalchemy import select, Column, Integer, String, ForeignKey, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, selectinload, joinedload

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/teach_easy"

Base = declarative_base()

# Data Models (Reordered)

class Course(Base):  # Moved to the top
    __tablename__ = 'courses'
    course_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    icon_id = Column(Integer, ForeignKey('icons.icon_id'), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    icon = relationship("Icon", backref="courses", lazy="joined")


class Icon(Base):
    __tablename__ = 'icons'
    icon_id = Column(Integer, primary_key=True)
    icon_name = Column(String, nullable=False, unique=True)
    link = Column(String, nullable=True)

class Teacher(Base):
    __tablename__ = 'teachers'
    teacher_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    portfolio = Column(String)
    password = Column(String, nullable=False)
    classes = relationship("Class", back_populates="teacher")
    courses = relationship("Course", back_populates="teacher")


class Subject(Base):
    __tablename__ = 'subjects'
    subject_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    classes = relationship("Class", back_populates="subject")


class Class(Base):
    __tablename__ = 'classes'
    class_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    class_time = Column(String, nullable=False)  # Changed to String for flexibility
    subject = relationship("Subject", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")


# Pydantic Input Models
class CourseInput(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(None, max_length=255)
    teacher_id: int = Field(..., gt=0)
    icon_id: int = Field(None, gt=0)  # Optional icon ID


class ClassInput(BaseModel):
    title: str = Field(..., max_length=100)
    subject_id: int = Field(..., gt=0)
    teacher_id: int = Field(..., gt=0)
    class_time: str = Field(...)

# Add to_dict method to the models
def _add_to_dict_method(cls):
    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for relationship_name, relationship_obj in inspect(self).relationships.items():
            if relationship_obj.lazy == "joined" and getattr(self, relationship_name):
                result[relationship_name] = getattr(self, relationship_name).to_dict()
        return result
    cls.to_dict = to_dict
    return cls

for model in (Teacher, Class, Subject, Course, Icon): #added icon to to_dict
    _add_to_dict_method(model)


# API Endpoints
async def get_courses(request):
    async with async_session_maker() as session:
        courses = await session.scalars(
            select(Course).options(joinedload(Course.icon))  # Use joinedload here
        )
        return web.json_response(
            [course.to_dict() for course in courses.all()]  # Iterate over results
        )

async def create_course(request):
    try:
        data = CourseInput(**await request.json())

        async with async_session_maker() as session:
            # Check if teacher exists
            teacher = await session.get(Teacher, data.teacher_id)
            if not teacher:
                raise web.HTTPNotFound(reason="Teacher not found")

            # Get icon if provided
            icon = None
            if data.icon_id:
                icon = await session.get(Icon, data.icon_id)
                if not icon:
                    raise web.HTTPBadRequest(reason="Icon with given ID does not exist")

            # Create course
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


async def create_class(request):  # Now, Class is defined before this function
    try:
        data = ClassInput(**await request.json())
        async with async_session_maker() as session:
            new_class = Class(**data.dict())
            session.add(new_class)
            await session.commit()
            return web.json_response(new_class.to_dict(), status=201)  # Return the created class as JSON
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

def _add_to_dict_method(cls):
    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Check for __mapper__ before accessing relationships
        if hasattr(self, '__mapper__'):
            for relationship_name, relationship_obj in inspect(self.__mapper__).relationships.items():
                if relationship_obj.lazy == "joined" and getattr(self, relationship_name):
                    result[relationship_name] = getattr(self, relationship_name).to_dict()
        return result
    cls.to_dict = to_dict
    return cls


# App Setup
app = web.Application()
app.add_routes([
    web.get('/courses', get_courses),
    web.post('/courses', create_course),
    web.post('/classes', create_class),
    web.get('/icons', get_icons),
    web.get('/courses/teacher/{teacher_id}', get_courses_by_teacher),
])

for model in (Teacher, Class, Subject, Course, Icon):
    _add_to_dict_method(model)


# Main Function (Modified)
async def main():
    # Create engine and session maker *inside* main to ensure correct initialization order
    global engine
    global async_session_maker
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        for model in (Teacher, Class, Subject, Course, Icon):
            _add_to_dict_method(model)

        await web._run_app(app, host='64.226.115.55', port=80)
    finally:
        await engine.dispose()  # Clean up the engine


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    asyncio.run(main())
