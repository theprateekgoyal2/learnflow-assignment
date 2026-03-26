from api.courses.apis import (
    create_course, list_courses, get_course, delete_course,
    add_module, add_video_lesson, add_quiz_lesson, add_pdf_lesson,
)

api_routes = [
    ("/", create_course, ["POST"]),
    ("/", list_courses, ["GET"]),
    ("/{course_id}", get_course, ["GET"]),
    ("/{course_id}", delete_course, ["DELETE"]),
    ("/{course_id}/modules", add_module, ["POST"]),
    ("/{course_id}/modules/{module_id}/lessons/video", add_video_lesson, ["POST"]),
    ("/{course_id}/modules/{module_id}/lessons/quiz", add_quiz_lesson, ["POST"]),
    ("/{course_id}/modules/{module_id}/lessons/pdf", add_pdf_lesson, ["POST"]),
]
