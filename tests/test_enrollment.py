"""Tests for enrollment business logic."""

import pytest

from core.exceptions import (
    AlreadyEnrolledError, CourseNotFoundError, NotEnrolledError,
    PermissionDeniedError, UserNotFoundError,
)
from api.users.models.users import UserTable


class TestEnrollment:

    def test_enroll_student_successfully(self, enrollment_service, sample_student, sample_course_with_lessons):
        record = enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        assert record.student_id == sample_student.id
        assert record.course_id == sample_course_with_lessons.id

    def test_enroll_raises_for_nonexistent_user(self, enrollment_service, sample_course_with_lessons):
        with pytest.raises(UserNotFoundError):
            enrollment_service.enroll("ghost", sample_course_with_lessons.id)

    def test_enroll_raises_for_nonexistent_course(self, enrollment_service, sample_student):
        with pytest.raises(CourseNotFoundError):
            enrollment_service.enroll(sample_student.id, "no-such-course")

    def test_enroll_raises_for_non_student_role(self, enrollment_service, sample_instructor, sample_course_with_lessons):
        with pytest.raises(PermissionDeniedError):
            enrollment_service.enroll(sample_instructor.id, sample_course_with_lessons.id)

    def test_double_enrollment_raises(self, enrollment_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        with pytest.raises(AlreadyEnrolledError):
            enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)

    def test_unenroll_successfully(self, enrollment_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        enrollment_service.unenroll(sample_student.id, sample_course_with_lessons.id)
        assert not enrollment_service.is_enrolled(sample_student.id, sample_course_with_lessons.id)

    def test_unenroll_raises_when_not_enrolled(self, enrollment_service, sample_student, sample_course_with_lessons):
        with pytest.raises(NotEnrolledError):
            enrollment_service.unenroll(sample_student.id, sample_course_with_lessons.id)

    def test_validate_access_passes_for_enrolled(self, enrollment_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        enrollment_service.validate_access(sample_student.id, sample_course_with_lessons.id)  # no raise

    def test_validate_access_raises_for_unenrolled(self, enrollment_service, sample_student, sample_course_with_lessons):
        with pytest.raises(NotEnrolledError):
            enrollment_service.validate_access(sample_student.id, sample_course_with_lessons.id)

    def test_get_enrolled_students(self, db, enrollment_service, sample_student, sample_course_with_lessons):
        student2 = UserTable(id="s2", name="Diana", email="diana@example.com", role="student")
        db.add(student2); db.commit()
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        enrollment_service.enroll(student2.id, sample_course_with_lessons.id)
        assert len(enrollment_service.get_enrolled_students(sample_course_with_lessons.id)) == 2

    def test_get_enrolled_students_includes_names(self, enrollment_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        rows = enrollment_service.get_enrolled_students(sample_course_with_lessons.id)
        _, student_name, course_name = rows[0]
        assert student_name == sample_student.name
        assert course_name == sample_course_with_lessons.title

    def test_get_student_courses_includes_course_name(self, enrollment_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        rows = enrollment_service.get_student_courses(sample_student.id)
        _, course_name = rows[0]
        assert course_name == sample_course_with_lessons.title
