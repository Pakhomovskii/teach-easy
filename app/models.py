from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()


class Course(Base):
    """
       Represents a course entity within the database, mapping to the 'courses' table.
       Attributes:
           course_id:
           title:
           description:
           teacher_id:
           icon_id:
           teacher:
           icon:
       """
    __tablename__ = 'courses'
    course_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    icon_id = Column(Integer, ForeignKey('icons.icon_id'), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    icon = relationship("Icon", backref="courses", lazy="joined")


class Icon(Base):
    """
        Represents an icon entity within the database, mapping to the 'icons' table.
        Attributes:
            icon_id
            icon_name
            link
        """
    __tablename__ = 'icons'
    icon_id = Column(Integer, primary_key=True)
    icon_name = Column(String, nullable=False, unique=True)
    link = Column(String, nullable=True)


class Teacher(Base):
    """
        Represents a teacher entity within the database, mapping to the 'teachers' table.
        Attributes:
            teacher_id
            name
            surname
            email
            portfolio
            password
            classes
            courses
    """
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
    """
        Represents a subject entity within the database, mapping to the 'subjects' table.
        Attributes:
            subject_id
            name
            course_id
            classes
        """
    __tablename__ = 'subjects'
    subject_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    classes = relationship("Class", back_populates="subject")


class Class(Base):
    """
        Represents a class entity within the database, mapping to the 'classes' table.
        Attributes:
            class_id
            title
            subject_id
            teacher_id
            class_time
            subject
            teacher
        """
    __tablename__ = 'classes'
    class_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=False)
    class_time = Column(String, nullable=False)
    subject = relationship("Subject", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")


class CourseInput(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(None, max_length=255)
    teacher_id: int = Field(..., gt=0)
    icon_id: int = Field(None, gt=0)


class Student(Base):
    """
        Represents a student entity within the database, mapping to the 'students' table.
        Attributes:
            student_id
            name (Column)
            surname (Column)
            email (Column)
            birthday (Column)
        """
    __tablename__ = 'students'
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    birthday = Column(String, nullable=False)


class ClassInput(BaseModel):
    """
        A Pydantic model representing the input data structure for a class entity.
        Attributes:
            title (str)
            subject_id (int)
            teacher_id (int)
            class_time (str)
        """
    title: str = Field(..., max_length=100)
    subject_id: int = Field(..., gt=0)
    teacher_id: int = Field(..., gt=0)
    class_time: str = Field(...)
