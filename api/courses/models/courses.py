from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from core.db import Base


class CourseTable(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    instructor_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    modules = relationship(
        "ModuleTable",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="ModuleTable.position",
    )


class ModuleTable(Base):
    __tablename__ = "modules"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)

    course = relationship("CourseTable", back_populates="modules")
    lessons = relationship(
        "LessonTable",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="LessonTable.position",
    )


class LessonTable(Base):
    """Single table for all lesson types.

    `content_type` is the discriminator ('video' | 'quiz' | 'pdf').
    `lesson_data` stores type-specific fields as JSON so adding a new lesson
    type (e.g. 'live_webinar') requires zero schema changes — just a new
    content_type value and the corresponding keys in lesson_data.
    """

    __tablename__ = "lessons"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    module_id = Column(String, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    lesson_data = Column(JSON, nullable=False, default=dict)  # type-specific payload

    module = relationship("ModuleTable", back_populates="lessons")
