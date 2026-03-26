"""Tests for progress tracking business logic."""

import pytest

from api.courses.models.courses import CourseTable
from core.exceptions import LessonNotFoundError, NotEnrolledError


class TestProgress:

    def test_complete_lesson(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "l-1")
        assert "l-1" in progress_service.get_completed_lessons(sample_student.id, sample_course_with_lessons.id)

    def test_completing_same_lesson_twice_is_idempotent(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "l-1")
        progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "l-1")
        assert len(progress_service.get_completed_lessons(sample_student.id, sample_course_with_lessons.id)) == 1

    def test_complete_lesson_raises_when_not_enrolled(self, progress_service, sample_student, sample_course_with_lessons):
        with pytest.raises(NotEnrolledError):
            progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "l-1")

    def test_complete_lesson_raises_for_invalid_lesson(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        with pytest.raises(LessonNotFoundError):
            progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "bad-id")

    def test_progress_zero_at_start(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        assert progress_service.get_progress_percentage(sample_student.id, sample_course_with_lessons.id) == 0.0

    def test_progress_partial_completion(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, "l-1")
        pct = progress_service.get_progress_percentage(sample_student.id, sample_course_with_lessons.id)
        assert pct == pytest.approx(33.33, abs=0.01)

    def test_progress_full_completion(self, enrollment_service, progress_service, sample_student, sample_course_with_lessons):
        enrollment_service.enroll(sample_student.id, sample_course_with_lessons.id)
        for lid in ("l-1", "l-2", "l-3"):
            progress_service.complete_lesson(sample_student.id, sample_course_with_lessons.id, lid)
        assert progress_service.get_progress_percentage(sample_student.id, sample_course_with_lessons.id) == 100.0

    def test_progress_raises_when_not_enrolled(self, progress_service, sample_student, sample_course_with_lessons):
        with pytest.raises(NotEnrolledError):
            progress_service.get_progress_percentage(sample_student.id, sample_course_with_lessons.id)

    def test_progress_empty_course_returns_100(self, db, enrollment_service, progress_service, sample_student, sample_instructor):
        empty = CourseTable(id="empty-c", title="Empty", description="No lessons", instructor_id=sample_instructor.id)
        db.add(empty); db.commit()
        enrollment_service.enroll(sample_student.id, "empty-c")
        assert progress_service.get_progress_percentage(sample_student.id, "empty-c") == 100.0
