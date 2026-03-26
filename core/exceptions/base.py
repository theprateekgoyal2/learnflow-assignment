"""Domain-specific exceptions for LearnFlow."""


class LearnFlowError(Exception):
    """Base exception for all LearnFlow errors."""


class NotEnrolledError(LearnFlowError):
    def __init__(self, student_id: str, course_id: str) -> None:
        super().__init__(
            f"Student '{student_id}' is not enrolled in course '{course_id}'."
        )
        self.student_id = student_id
        self.course_id = course_id


class AlreadyEnrolledError(LearnFlowError):
    def __init__(self, student_id: str, course_id: str) -> None:
        super().__init__(
            f"Student '{student_id}' is already enrolled in course '{course_id}'."
        )


class CourseNotFoundError(LearnFlowError):
    def __init__(self, course_id: str) -> None:
        super().__init__(f"Course '{course_id}' not found.")
        self.course_id = course_id


class UserNotFoundError(LearnFlowError):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User '{user_id}' not found.")
        self.user_id = user_id


class PermissionDeniedError(LearnFlowError):
    def __init__(self, message: str = "Permission denied.") -> None:
        super().__init__(message)


class CourseHasActiveStudentsError(LearnFlowError):
    def __init__(self, course_id: str, student_count: int) -> None:
        super().__init__(
            f"Cannot delete course '{course_id}': "
            f"{student_count} student(s) are currently enrolled."
        )
        self.course_id = course_id
        self.student_count = student_count


class LessonNotFoundError(LearnFlowError):
    def __init__(self, lesson_id: str, course_id: str) -> None:
        super().__init__(
            f"Lesson '{lesson_id}' not found in course '{course_id}'."
        )
