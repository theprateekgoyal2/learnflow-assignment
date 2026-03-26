from api.progress.apis import complete_lesson, get_progress

api_routes = [
    ("/complete", complete_lesson, ["POST"]),
    ("/{student_id}/{course_id}", get_progress,  ["GET"]),
]
