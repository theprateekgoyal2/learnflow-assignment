from api.enrollment.apis import enroll, unenroll, get_student_enrollments, get_course_enrollments

api_routes = [
    ("/", enroll, ["POST"]),
    ("/{student_id}/{course_id}", unenroll, ["DELETE"]),
    ("/students/{student_id}", get_student_enrollments, ["GET"]),
    ("/courses/{course_id}", get_course_enrollments, ["GET"]),
]
