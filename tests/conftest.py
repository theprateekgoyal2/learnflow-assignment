"""Shared fixtures — each test gets a clean SQLite ':memory:' database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.db import Base
import api.users.models.users          # noqa: F401 — register models with Base
import api.courses.models.courses      # noqa: F401
import api.enrollment.models.enrollment  # noqa: F401

from api.users.models.users import UserTable
from api.courses.models.courses import CourseTable, ModuleTable, LessonTable
from api.courses.services.course_service import CourseService
from api.enrollment.services.enrollment_service import EnrollmentService
from api.progress.services.progress_service import ProgressService


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def enrollment_service(db): return EnrollmentService(db)

@pytest.fixture
def progress_service(db): return ProgressService(db)

@pytest.fixture
def course_service(db): return CourseService(db)


@pytest.fixture
def sample_student(db) -> UserTable:
    u = UserTable(id="student-1", name="Alice", email="alice@example.com", role="student")
    db.add(u); db.commit(); return u

@pytest.fixture
def sample_instructor(db) -> UserTable:
    u = UserTable(id="instructor-1", name="Bob", email="bob@example.com", role="instructor")
    db.add(u); db.commit(); return u

@pytest.fixture
def sample_admin(db) -> UserTable:
    u = UserTable(id="admin-1", name="Charlie", email="charlie@example.com", role="admin")
    db.add(u); db.commit(); return u


@pytest.fixture
def sample_course_with_lessons(db, sample_instructor) -> CourseTable:
    """Course → 2 modules → 3 lessons total."""
    course = CourseTable(id="course-1", title="Python 101", description="Intro", instructor_id=sample_instructor.id)
    db.add(course)

    mod1 = ModuleTable(id="mod-1", title="Basics", course_id="course-1", position=0)
    mod2 = ModuleTable(id="mod-2", title="Advanced", course_id="course-1", position=1)
    db.add_all([mod1, mod2])

    db.add_all([
        LessonTable(id="l-1", title="Variables", content_type="video",  module_id="mod-1", position=0, lesson_data={"video_url": "https://v.io/1", "duration_minutes": 10}),
        LessonTable(id="l-2", title="Quiz 1",    content_type="quiz",   module_id="mod-1", position=1, lesson_data={"questions": []}),
        LessonTable(id="l-3", title="Decorators", content_type="pdf",   module_id="mod-2", position=0, lesson_data={"pdf_url": "https://p.io/1", "page_count": 5}),
    ])
    db.commit()
    db.refresh(course)
    return course
