from __future__ import annotations

from pydantic import BaseModel


class CompleteLessonIn(BaseModel):
    student_id: str
    course_id: str
    lesson_id: str


class CompleteLessonOut(BaseModel):
    student_name: str
    course_name: str
    lesson_id: str
    message: str


class ProgressOut(BaseModel):
    student_id: str
    student_name: str
    course_id: str
    course_name: str
    percentage: float
    completed_lessons: int
    total_lessons: int
