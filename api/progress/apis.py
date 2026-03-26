from fastapi import Depends
from sqlalchemy.orm import Session

from api.progress.request.progress import CompleteLessonIn, CompleteLessonOut, ProgressOut
from api.progress.services.progress_service import ProgressService
from api.response import MessageOut
from core.db import get_db


async def complete_lesson(payload: CompleteLessonIn, db: Session = Depends(get_db)) -> CompleteLessonOut:
    student_name, course_name = ProgressService(db).complete_lesson(payload.student_id, payload.course_id, payload.lesson_id)
    return CompleteLessonOut(
        student_name=student_name,
        course_name=course_name,
        lesson_id=payload.lesson_id,
        message="Lesson marked complete.",
    )


async def get_progress(student_id: str, course_id: str, db: Session = Depends(get_db)) -> ProgressOut:
    svc = ProgressService(db)
    student_name, course_name = svc.get_names(student_id, course_id)
    percentage = svc.get_progress_percentage(student_id, course_id)
    completed = svc.get_completed_lessons(student_id, course_id)
    total = svc.get_total_lessons(course_id)
    return ProgressOut(
        student_id=student_id, student_name=student_name,
        course_id=course_id, course_name=course_name,
        percentage=percentage, completed_lessons=len(completed), total_lessons=total,
    )
