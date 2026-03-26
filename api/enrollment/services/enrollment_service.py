from sqlalchemy.orm import Session

from api.courses.models.courses import CourseTable
from api.enrollment.models.enrollment import EnrollmentTable
from api.users.models.users import UserTable
from core.exceptions import (
    AlreadyEnrolledError,
    CourseNotFoundError,
    NotEnrolledError,
    PermissionDeniedError,
    UserNotFoundError,
)


class EnrollmentService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def enroll(self, student_id: str, course_id: str) -> EnrollmentTable:
        user = self.db.query(UserTable).filter(UserTable.id == student_id).first()
        if not user:
            raise UserNotFoundError(student_id)
        if user.role != "student":
            raise PermissionDeniedError("Only students can enroll in courses.")

        if not self.db.query(CourseTable).filter(CourseTable.id == course_id).first():
            raise CourseNotFoundError(course_id)

        if self._get_enrollment(student_id, course_id):
            raise AlreadyEnrolledError(student_id, course_id)

        enrollment = EnrollmentTable(student_id=student_id, course_id=course_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def unenroll(self, student_id: str, course_id: str) -> None:
        enrollment = self._get_enrollment(student_id, course_id)
        if not enrollment:
            raise NotEnrolledError(student_id, course_id)
        self.db.delete(enrollment)
        self.db.commit()

    def is_enrolled(self, student_id: str, course_id: str) -> bool:
        return self._get_enrollment(student_id, course_id) is not None

    def validate_access(self, student_id: str, course_id: str) -> None:
        if not self.is_enrolled(student_id, course_id):
            raise NotEnrolledError(student_id, course_id)

    def get_enrolled_students(self, course_id: str) -> list[tuple[EnrollmentTable, str, str]]:
        return (
            self.db.query(EnrollmentTable, UserTable.name, CourseTable.title)
            .join(UserTable, UserTable.id == EnrollmentTable.student_id)
            .join(CourseTable, CourseTable.id == EnrollmentTable.course_id)
            .filter(EnrollmentTable.course_id == course_id)
            .all()
        )

    def get_student_courses(self, student_id: str) -> list[tuple[EnrollmentTable, str]]:
        rows = (
            self.db.query(EnrollmentTable, CourseTable.title)
            .join(CourseTable, CourseTable.id == EnrollmentTable.course_id)
            .filter(EnrollmentTable.student_id == student_id)
            .all()
        )
        return rows

    def _get_enrollment(self, student_id: str, course_id: str) -> EnrollmentTable | None:
        return (
            self.db.query(EnrollmentTable)
            .filter(
                EnrollmentTable.student_id == student_id,
                EnrollmentTable.course_id == course_id,
            )
            .first()
        )
