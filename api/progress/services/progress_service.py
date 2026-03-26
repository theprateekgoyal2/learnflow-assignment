from sqlalchemy import func
from sqlalchemy.orm import Session

from api.courses.models.courses import CourseTable, LessonTable, ModuleTable
from api.enrollment.models.enrollment import EnrollmentTable, LessonCompletionTable
from api.users.models.users import UserTable
from core.exceptions import CourseNotFoundError, LessonNotFoundError, NotEnrolledError


class ProgressService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def complete_lesson(self, student_id: str, course_id: str, lesson_id: str) -> tuple[str, str]:
        """Mark a lesson complete. Calling twice is safe — PK uniqueness makes it idempotent.
        Returns (student_name, course_name)."""
        student_name = self.db.query(UserTable.name).filter(UserTable.id == student_id).scalar() or student_id
        course_name = self.db.query(CourseTable.title).filter(CourseTable.id == course_id).scalar() or course_id

        if not self._get_enrollment(student_id, course_id):
            raise NotEnrolledError(student_name, course_name)

        lesson_exists = (
            self.db.query(LessonTable)
            .join(ModuleTable)
            .filter(LessonTable.id == lesson_id, ModuleTable.course_id == course_id)
            .first()
        )
        if not lesson_exists:
            raise LessonNotFoundError(lesson_id, course_name)

        already_done = (
            self.db.query(LessonCompletionTable)
            .filter(
                LessonCompletionTable.student_id == student_id,
                LessonCompletionTable.course_id == course_id,
                LessonCompletionTable.lesson_id == lesson_id,
            )
            .first()
        )
        if not already_done:
            self.db.add(LessonCompletionTable(student_id=student_id, course_id=course_id, lesson_id=lesson_id))
            self.db.commit()

        return student_name, course_name

    def get_completed_lessons(self, student_id: str, course_id: str) -> set[str]:
        if not self._get_enrollment(student_id, course_id):
            raise NotEnrolledError(student_id, course_id)
        rows = (
            self.db.query(LessonCompletionTable.lesson_id)
            .filter(
                LessonCompletionTable.student_id == student_id,
                LessonCompletionTable.course_id == course_id,
            )
            .all()
        )
        return {r.lesson_id for r in rows}

    def get_progress_percentage(self, student_id: str, course_id: str) -> float:
        """Returns 0.0–100.0. An empty course counts as 100% complete."""
        if not self._get_enrollment(student_id, course_id):
            raise NotEnrolledError(student_id, course_id)

        total = (
            self.db.query(func.count(LessonTable.id))
            .join(ModuleTable)
            .filter(ModuleTable.course_id == course_id)
            .scalar()
        )
        if total == 0:
            return 100.0

        completed = (
            self.db.query(func.count(LessonCompletionTable.lesson_id))
            .filter(
                LessonCompletionTable.student_id == student_id,
                LessonCompletionTable.course_id == course_id,
            )
            .scalar()
        )
        return round((completed / total) * 100, 2)

    def get_names(self, student_id: str, course_id: str) -> tuple[str, str]:
        student_name = self.db.query(UserTable.name).filter(UserTable.id == student_id).scalar() or student_id
        course_name = self.db.query(CourseTable.title).filter(CourseTable.id == course_id).scalar() or course_id
        return student_name, course_name

    def get_total_lessons(self, course_id: str) -> int:
        return (
            self.db.query(func.count(LessonTable.id))
            .join(ModuleTable)
            .filter(ModuleTable.course_id == course_id)
            .scalar()
        )

    def _get_enrollment(self, student_id: str, course_id: str) -> EnrollmentTable | None:
        return (
            self.db.query(EnrollmentTable)
            .filter(
                EnrollmentTable.student_id == student_id,
                EnrollmentTable.course_id == course_id,
            )
            .first()
        )
