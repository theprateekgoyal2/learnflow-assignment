from fastapi import Depends
from sqlalchemy.orm import Session

from api.enrollment.request.enrollment import EnrollIn, EnrollmentOut
from api.enrollment.services.enrollment_service import EnrollmentService
from api.response import MessageOut
from core.db import get_db


def _out(r, course_name: str = "", student_name: str = "") -> EnrollmentOut:
    return EnrollmentOut(student_id=r.student_id, course_id=r.course_id, student_name=student_name, course_name=course_name, completed_lesson_ids=[])


async def enroll(payload: EnrollIn, db: Session = Depends(get_db)) -> EnrollmentOut:
    record = EnrollmentService(db).enroll(payload.student_id, payload.course_id)
    return _out(record)


async def unenroll(student_id: str, course_id: str, db: Session = Depends(get_db)) -> MessageOut:
    EnrollmentService(db).unenroll(student_id, course_id)
    return MessageOut(message=f"Student '{student_id}' unenrolled from course '{course_id}'.")


async def get_student_enrollments(student_id: str, db: Session = Depends(get_db)) -> list[EnrollmentOut]:
    return [_out(r, course_name) for r, course_name in EnrollmentService(db).get_student_courses(student_id)]


async def get_course_enrollments(course_id: str, db: Session = Depends(get_db)) -> list[EnrollmentOut]:
    return [
        _out(r, course_name=course_name, student_name=student_name)
        for r, student_name, course_name in EnrollmentService(db).get_enrolled_students(course_id)
    ]
