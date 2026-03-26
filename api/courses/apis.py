from fastapi import Depends
from sqlalchemy.orm import Session

from api.courses.request.courses import (
    AddModuleIn, AddPDFLessonIn, AddQuizLessonIn, AddVideoLessonIn,
    CourseDetailOut, CourseOut, CreateCourseIn, LessonOut, ModuleOut,
)
from api.courses.services.course_service import CourseService
from api.response import MessageOut
from core.db import get_db


def _lesson_out(l) -> LessonOut:
    return LessonOut(id=l.id, title=l.title, content_type=l.content_type)


def _detail_out(course) -> CourseDetailOut:
    return CourseDetailOut(
        id=course.id, title=course.title, description=course.description,
        instructor_id=course.instructor_id,
        modules=[
            ModuleOut(id=m.id, title=m.title, lessons=[_lesson_out(l) for l in m.lessons])
            for m in course.modules
        ],
    )


async def create_course(payload: CreateCourseIn, db: Session = Depends(get_db)) -> CourseOut:
    c = CourseService(db).create_course(payload.instructor_id, payload.title, payload.description)
    return CourseOut(id=c.id, title=c.title, description=c.description, instructor_id=c.instructor_id)


async def list_courses(db: Session = Depends(get_db)) -> list[CourseOut]:
    return [CourseOut(id=c.id, title=c.title, description=c.description, instructor_id=c.instructor_id)
            for c in CourseService(db).list_courses()]


async def get_course(course_id: str, db: Session = Depends(get_db)) -> CourseDetailOut:
    return _detail_out(CourseService(db).get_course(course_id))


async def delete_course(course_id: str, requester_id: str, db: Session = Depends(get_db)) -> MessageOut:
    """requester_id as query param — would come from JWT in production."""
    CourseService(db).delete_course(requester_id, course_id)
    return MessageOut(message=f"Course '{course_id}' deleted.")


async def add_module(course_id: str, payload: AddModuleIn, db: Session = Depends(get_db)) -> ModuleOut:
    m = CourseService(db).add_module(course_id, payload.title)
    return ModuleOut(id=m.id, title=m.title, lessons=[])


async def add_video_lesson(course_id: str, module_id: str, payload: AddVideoLessonIn, db: Session = Depends(get_db)) -> LessonOut:
    l = CourseService(db).add_lesson(course_id, module_id, payload.title, "video",
                                     {"video_url": payload.video_url, "duration_minutes": payload.duration_minutes})
    return LessonOut(id=l.id, title=l.title, content_type=l.content_type)


async def add_quiz_lesson(course_id: str, module_id: str, payload: AddQuizLessonIn, db: Session = Depends(get_db)) -> LessonOut:
    l = CourseService(db).add_lesson(course_id, module_id, payload.title, "quiz",
                                     {"questions": payload.questions})
    return LessonOut(id=l.id, title=l.title, content_type=l.content_type)


async def add_pdf_lesson(course_id: str, module_id: str, payload: AddPDFLessonIn, db: Session = Depends(get_db)) -> LessonOut:
    l = CourseService(db).add_lesson(course_id, module_id, payload.title, "pdf",
                                     {"pdf_url": payload.pdf_url, "page_count": payload.page_count})
    return LessonOut(id=l.id, title=l.title, content_type=l.content_type)
