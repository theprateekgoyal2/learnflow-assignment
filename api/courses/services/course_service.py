from uuid import uuid4

from sqlalchemy.orm import Session

from api.courses.models.courses import CourseTable, LessonTable, ModuleTable
from api.enrollment.models.enrollment import EnrollmentTable
from api.users.models.users import UserTable
from core.exceptions import (
    CourseHasActiveStudentsError,
    CourseNotFoundError,
    PermissionDeniedError,
    UserNotFoundError,
)
from models.lesson import PDFLesson, QuizLesson, VideoLesson

_LESSON_FACTORY = {
    "video": lambda title, data: VideoLesson(title, data["video_url"], data["duration_minutes"]),
    "quiz": lambda title, data: QuizLesson(title, data["questions"]),
    "pdf": lambda title, data: PDFLesson(title, data["pdf_url"], data["page_count"]),
}


class CourseService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_course(self, instructor_id: str, title: str, description: str) -> CourseTable:
        user = self.db.query(UserTable).filter(UserTable.id == instructor_id).first()
        if not user:
            raise UserNotFoundError(instructor_id)
        if user.role not in ("instructor", "admin"):
            raise PermissionDeniedError("Only instructors or admins can create courses.")

        course = CourseTable(id=str(uuid4()), title=title, description=description, instructor_id=instructor_id)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete_course(self, requester_id: str, course_id: str) -> None:
        user = self.db.query(UserTable).filter(UserTable.id == requester_id).first()
        if not user:
            raise UserNotFoundError(requester_id)

        course = self.db.query(CourseTable).filter(CourseTable.id == course_id).first()
        if not course:
            raise CourseNotFoundError(course_id)

        if user.role == "student":
            raise PermissionDeniedError("Students cannot delete courses.")
        if user.role == "instructor" and course.instructor_id != requester_id:
            raise PermissionDeniedError("Instructors can only delete their own courses.")

        enrolled_count = (
            self.db.query(EnrollmentTable)
            .filter(EnrollmentTable.course_id == course_id)
            .count()
        )
        if enrolled_count > 0:
            raise CourseHasActiveStudentsError(course_id, enrolled_count)

        self.db.delete(course)
        self.db.commit()

    def add_module(self, course_id: str, title: str) -> ModuleTable:
        course = self.db.query(CourseTable).filter(CourseTable.id == course_id).first()
        if not course:
            raise CourseNotFoundError(course_id)

        position = len(course.modules)
        module = ModuleTable(id=str(uuid4()), title=title, course_id=course_id, position=position)
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def add_lesson(self, course_id: str, module_id: str, title: str, content_type: str, lesson_data: dict) -> LessonTable:
        module = (
            self.db.query(ModuleTable)
            .filter(ModuleTable.id == module_id, ModuleTable.course_id == course_id)
            .first()
        )
        if not module:
            raise CourseNotFoundError(f"Module '{module_id}' not found in course '{course_id}'.")

        # Build domain model first — ABC enforces content_type contract and validates fields.
        # Adding a new lesson type only requires a new Lesson subclass + factory entry.
        factory = _LESSON_FACTORY.get(content_type)
        if not factory:
            raise ValueError(f"Unknown content_type: '{content_type}'.")
        domain_lesson = factory(title, lesson_data)

        position = len(module.lessons)
        lesson = LessonTable(
            id=domain_lesson.id,
            title=domain_lesson.title,
            content_type=domain_lesson.content_type,
            module_id=module_id,
            position=position,
            lesson_data=lesson_data,
        )
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_course(self, course_id: str) -> CourseTable:
        course = self.db.query(CourseTable).filter(CourseTable.id == course_id).first()
        if not course:
            raise CourseNotFoundError(course_id)
        return course

    def list_courses(self) -> list[CourseTable]:
        return self.db.query(CourseTable).all()
