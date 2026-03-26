# LearnFlow — LMS Core Backend

A Learning Management System backend built with Python, FastAPI, and SQLAlchemy, demonstrating OOP principles, SOLID design, and clean layered architecture.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Run all tests
pytest -v
```

Server starts at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Project Structure

```
learnflow/
├── main.py                   # Entry point (uvicorn)
├── requirements.txt
├── models/                   # Domain layer (pure Python, no I/O)
│   └── lesson.py             # Lesson ABC, VideoLesson, QuizLesson, PDFLesson
├── core/
│   ├── config.py             # Environment config
│   ├── db/session.py         # SQLAlchemy engine, SessionLocal, get_db
│   └── exceptions/base.py    # Domain exceptions
├── api/
│   ├── server.py             # App factory, CORS, exception handlers
│   ├── __init__.py           # Central router
│   ├── users/
│   │   ├── models/users.py   # UserTable (ORM)
│   │   ├── services/user_service.py
│   │   ├── request/users.py  # Pydantic schemas
│   │   └── apis.py           # FastAPI handlers
│   ├── courses/
│   │   ├── models/courses.py # CourseTable, ModuleTable, LessonTable (ORM)
│   │   ├── services/course_service.py
│   │   ├── request/courses.py
│   │   └── apis.py
│   ├── enrollment/
│   │   ├── models/enrollment.py  # EnrollmentTable, LessonCompletionTable (ORM)
│   │   ├── services/enrollment_service.py
│   │   ├── request/enrollment.py
│   │   └── apis.py
│   └── progress/
│       ├── services/progress_service.py
│       ├── request/progress.py
│       └── apis.py
└── tests/
    ├── conftest.py           # SQLite :memory: fixtures
    ├── test_users.py
    ├── test_course.py
    ├── test_enrollment.py
    └── test_progress.py
```

## API Endpoints

| Method | Path | Description | Response includes |
|---|---|---|---|
| POST | `/users/students` | Create student | `id`, `name`, `email`, `role` |
| POST | `/users/instructors` | Create instructor | `id`, `name`, `email`, `role` |
| GET | `/users/{user_id}` | Get user | `id`, `name`, `email`, `role` |
| GET | `/users/` | List all users | array of users |
| POST | `/courses/` | Create course | `id`, `title`, `description`, `instructor_id` |
| GET | `/courses/` | List all courses | array of courses |
| GET | `/courses/{course_id}` | Get course with modules/lessons | full nested structure |
| DELETE | `/courses/{course_id}` | Delete course | confirmation message |
| POST | `/courses/{course_id}/modules` | Add module | `id`, `title` |
| POST | `/courses/{course_id}/modules/{module_id}/lessons/video` | Add video lesson | `id`, `title`, `content_type` |
| POST | `/courses/{course_id}/modules/{module_id}/lessons/quiz` | Add quiz lesson | `id`, `title`, `content_type` |
| POST | `/courses/{course_id}/modules/{module_id}/lessons/pdf` | Add PDF lesson | `id`, `title`, `content_type` |
| POST | `/enrollments/` | Enroll student | `student_id`, `course_id` |
| DELETE | `/enrollments/{student_id}/{course_id}` | Unenroll student | confirmation message |
| GET | `/enrollments/students/{student_id}` | Get student's enrolled courses | includes `course_name` |
| GET | `/enrollments/courses/{course_id}` | Get students enrolled in a course | includes `student_name`, `course_name` |
| POST | `/progress/complete` | Mark lesson complete | `student_name`, `course_name`, `lesson_id`, `message` |
| GET | `/progress/{student_id}/{course_id}` | Get progress percentage | `student_name`, `course_name`, `percentage`, `completed_lessons`, `total_lessons` |

## Design Decisions

### 1. Two-Layer Model Design

The project has two distinct model layers, each with a different purpose:

| Layer | Location | Purpose |
|---|---|---|
| **Domain models** | `models/` | Pure Python — business identity, validation, OOP hierarchy |
| **ORM models** | `api/*/models/` | SQLAlchemy tables — persistence only |

Services sit between the two layers. When creating a lesson, `CourseService` first constructs the domain model (which validates the data and asserts the content_type contract), then maps it to the ORM table for storage.

### 2. Abstract Base Class for Lessons (Open/Closed Principle)

`Lesson` is an ABC that enforces a `content_type` property on every subclass.

```python
class Lesson(ABC):
    @property
    @abstractmethod
    def content_type(self) -> str: ...

class VideoLesson(Lesson):
    @property
    def content_type(self) -> str:
        return "video"
```

To add a new lesson type (e.g., `LiveWebinarLesson`), you:

1. Create a subclass of `Lesson` in `models/lesson.py`.
2. Implement the `content_type` property.
3. Add one entry to `_LESSON_FACTORY` in `course_service.py`.

**No other existing code changes.** The enrollment, progress, and course services all remain untouched.

**Why ABC over Mixins?** Every lesson shares a mandatory identity contract — a unique id, a title, and a content_type. An ABC enforces this at class-definition time: if a subclass omits `content_type`, Python raises `TypeError` immediately on instantiation. Mixins would be appropriate for optional, composable behaviors (e.g., "downloadable" + "gradeable"), but here the requirement is a uniform, non-optional interface. ABC is the right tool.

### 3. Dependency Injection via `Depends(get_db)`

Each FastAPI handler receives a fresh SQLAlchemy `Session` via `Depends(get_db)`. Services are instantiated inline — `CourseService(db).create_course(...)` — rather than being attached to app state. This is the FastAPI-idiomatic approach:

- **Testable**: Tests inject a `:memory:` session directly into services.
- **Scoped**: Session opens and closes per request; no shared state between requests.

### 4. Access Control & Edge Cases

| Scenario | Behavior |
|---|---|
| Student accesses unenrolled course | `NotEnrolledError` |
| Student enrolls twice | `AlreadyEnrolledError` |
| Student completes same lesson twice | Idempotent — ignored (composite PK) |
| Instructor deletes course with active students | `CourseHasActiveStudentsError` |
| Instructor deletes another instructor's course | `PermissionDeniedError` |
| Student tries to create a course | `PermissionDeniedError` |


## System Design (UML)

```
┌──────────────────────────────────────────────────────────┐
│                     HTTP Layer (FastAPI)                  │
│          api/*/apis.py  +  Pydantic schemas               │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                     Service Layer                         │
│   CourseService  EnrollmentService  ProgressService       │
│         │                                                 │
│         │  constructs domain model, then maps to ORM      │
│         ▼                                                 │
│   ┌─────────────────────────────────────┐                 │
│   │         Domain Layer (models/)      │                 │
│   │                                     │                 │
│   │  «Lesson ABC»                       │                 │
│   │    ├── VideoLesson                  │                 │
│   │    ├── QuizLesson                   │                 │
│   │    └── PDFLesson                    │                 │
│   │                                     │                 │
│   │  Course ──► Module ──► Lesson       │                 │
│   └─────────────────────────────────────┘                 │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                      ORM Layer (SQLAlchemy)               │
│   UserTable  CourseTable  ModuleTable  LessonTable        │
│   EnrollmentTable  LessonCompletionTable                  │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                       SQLite (learnflow.db)
```

## Adding a New Lesson Type

Example: adding a `LiveWebinarLesson`:

```python
# models/lesson.py
class LiveWebinarLesson(Lesson):
    def __init__(self, title: str, meeting_url: str, scheduled_at: str) -> None:
        super().__init__(title)
        self.meeting_url = meeting_url
        self.scheduled_at = scheduled_at

    @property
    def content_type(self) -> str:
        return "live_webinar"
```

```python
# api/courses/services/course_service.py — add one entry to the factory
_LESSON_FACTORY = {
    ...
    "live_webinar": lambda title, data: LiveWebinarLesson(title, data["meeting_url"], data["scheduled_at"]),
}
```

Add a route in `routes.py`, a handler in `apis.py`, and a Pydantic schema in `request/courses.py`. No other code changes needed.
