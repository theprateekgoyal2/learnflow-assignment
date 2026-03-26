from __future__ import annotations

from pydantic import BaseModel


class CreateCourseIn(BaseModel):
    title: str
    description: str
    instructor_id: str


class AddModuleIn(BaseModel):
    title: str


class AddVideoLessonIn(BaseModel):
    title: str
    video_url: str
    duration_minutes: int


class AddQuizLessonIn(BaseModel):
    title: str
    questions: list[dict[str, str]]


class AddPDFLessonIn(BaseModel):
    title: str
    pdf_url: str
    page_count: int


class LessonOut(BaseModel):
    id: str
    title: str
    content_type: str


class ModuleOut(BaseModel):
    id: str
    title: str
    lessons: list[LessonOut]


class CourseOut(BaseModel):
    id: str
    title: str
    description: str
    instructor_id: str


class CourseDetailOut(BaseModel):
    id: str
    title: str
    description: str
    instructor_id: str
    modules: list[ModuleOut]
