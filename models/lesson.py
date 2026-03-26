"""Lesson models using Abstract Base Class for extensibility.

We use an ABC because every lesson must satisfy the same interface — a
consistent identity and a content_type. Adding a new lesson type (e.g.,
LiveWebinarLesson) requires only a new subclass; no existing code changes.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod


class Lesson(ABC):
    def __init__(self, title: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.title = title

    @property
    @abstractmethod
    def content_type(self) -> str:
        """String identifier for this lesson type."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, title={self.title!r})"


class VideoLesson(Lesson):
    def __init__(self, title: str, video_url: str, duration_minutes: int) -> None:
        super().__init__(title)
        self.video_url = video_url
        self.duration_minutes = duration_minutes

    @property
    def content_type(self) -> str:
        return "video"


class QuizLesson(Lesson):
    def __init__(self, title: str, questions: list[dict[str, str]]) -> None:
        super().__init__(title)
        self.questions = questions

    @property
    def content_type(self) -> str:
        return "quiz"


class PDFLesson(Lesson):
    def __init__(self, title: str, pdf_url: str, page_count: int) -> None:
        super().__init__(title)
        self.pdf_url = pdf_url
        self.page_count = page_count

    @property
    def content_type(self) -> str:
        return "pdf"
