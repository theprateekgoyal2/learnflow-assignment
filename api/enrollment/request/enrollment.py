from __future__ import annotations

from pydantic import BaseModel


class EnrollIn(BaseModel):
    student_id: str
    course_id: str


class EnrollmentOut(BaseModel):
    student_id: str
    course_id: str
    student_name: str = ""
    course_name: str = ""
    completed_lesson_ids: list[str]
