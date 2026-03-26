"""Tests for course management business logic."""

import pytest

from api.users.models.users import UserTable
from core.exceptions import (
    CourseHasActiveStudentsError, CourseNotFoundError,
    PermissionDeniedError, UserNotFoundError,
)


class TestCourseService:

    def test_create_course_as_instructor(self, course_service, sample_instructor):
        c = course_service.create_course(sample_instructor.id, "Django Mastery", "Advanced Django")
        assert c.title == "Django Mastery"
        assert c.instructor_id == sample_instructor.id

    def test_create_course_as_admin(self, course_service, sample_admin):
        c = course_service.create_course(sample_admin.id, "Admin Course", "Created by admin")
        assert c.title == "Admin Course"

    def test_create_course_as_student_raises(self, course_service, sample_student):
        with pytest.raises(PermissionDeniedError):
            course_service.create_course(sample_student.id, "Nope", "Students cannot create")

    def test_create_course_nonexistent_user_raises(self, course_service):
        with pytest.raises(UserNotFoundError):
            course_service.create_course("ghost", "Title", "Desc")

    def test_delete_course_by_instructor(self, db, course_service, sample_instructor):
        c = course_service.create_course(sample_instructor.id, "Temp", "To delete")
        course_service.delete_course(sample_instructor.id, c.id)
        assert course_service.db.query(__import__("api.courses.models.courses", fromlist=["CourseTable"]).CourseTable).filter_by(id=c.id).first() is None

    def test_delete_course_by_admin(self, course_service, sample_instructor, sample_admin):
        c = course_service.create_course(sample_instructor.id, "Temp", "Admin deletes")
        course_service.delete_course(sample_admin.id, c.id)

    def test_delete_course_with_active_students_raises(self, course_service, enrollment_service, sample_instructor, sample_student):
        c = course_service.create_course(sample_instructor.id, "Popular", "Has students")
        enrollment_service.enroll(sample_student.id, c.id)
        with pytest.raises(CourseHasActiveStudentsError):
            course_service.delete_course(sample_instructor.id, c.id)

    def test_delete_nonexistent_course_raises(self, course_service, sample_instructor):
        with pytest.raises(CourseNotFoundError):
            course_service.delete_course(sample_instructor.id, "nope")

    def test_student_cannot_delete_course(self, course_service, sample_instructor, sample_student):
        c = course_service.create_course(sample_instructor.id, "Locked", "Students cannot touch")
        with pytest.raises(PermissionDeniedError):
            course_service.delete_course(sample_student.id, c.id)

    def test_instructor_cannot_delete_other_instructors_course(self, db, course_service, sample_instructor):
        other = UserTable(id="other-i", name="Eve", email="eve@example.com", role="instructor")
        db.add(other); db.commit()
        c = course_service.create_course(sample_instructor.id, "Bob Course", "Bob owns this")
        with pytest.raises(PermissionDeniedError):
            course_service.delete_course(other.id, c.id)

    def test_add_module_and_lesson_persists(self, course_service, sample_instructor):
        c = course_service.create_course(sample_instructor.id, "Modular", "Test modules")
        m = course_service.add_module(c.id, "Week 1")
        l = course_service.add_lesson(c.id, m.id, "Intro Video", "video",
                                       {"video_url": "https://v.io/1", "duration_minutes": 15})
        assert l.title == "Intro Video"
        assert l.content_type == "video"
