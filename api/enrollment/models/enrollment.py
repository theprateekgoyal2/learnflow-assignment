from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint, String

from core.db import Base


class EnrollmentTable(Base):
    __tablename__ = "enrollments"

    student_id = Column(String, ForeignKey("users.id"), primary_key=True)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LessonCompletionTable(Base):
    """Tracks which lessons a student has completed within a course enrollment.

    Completing the same lesson twice is a no-op — the primary key enforces
    uniqueness so we can safely do add + commit without a prior existence check.
    """

    __tablename__ = "lesson_completions"

    student_id = Column(String, primary_key=True)
    course_id = Column(String, primary_key=True)
    lesson_id = Column(String, ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "course_id"],
            ["enrollments.student_id", "enrollments.course_id"],
            ondelete="CASCADE",
        ),
    )
