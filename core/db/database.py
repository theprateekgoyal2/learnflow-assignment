"""SQLite database bootstrap — schema creation and connection management."""

import sqlite3

_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    role        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id             TEXT PRIMARY KEY,
    title          TEXT NOT NULL,
    description    TEXT NOT NULL,
    instructor_id  TEXT NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS modules (
    id         TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    course_id  TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lessons (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    content_type  TEXT NOT NULL,
    module_id     TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    position      INTEGER NOT NULL DEFAULT 0,
    metadata      TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS enrollments (
    student_id  TEXT NOT NULL REFERENCES users(id),
    course_id   TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, course_id)
);

CREATE TABLE IF NOT EXISTS lesson_completions (
    student_id  TEXT NOT NULL,
    course_id   TEXT NOT NULL,
    lesson_id   TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, course_id, lesson_id),
    FOREIGN KEY (student_id, course_id) REFERENCES enrollments(student_id, course_id)
        ON DELETE CASCADE
);
"""


class Database:
    """Thin wrapper around a SQLite connection.

    Accepts any valid SQLite path, including ':memory:' for tests.
    """

    def __init__(self, path: str = "learnflow.db") -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        self._conn.close()
