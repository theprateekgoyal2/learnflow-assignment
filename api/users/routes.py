from api.users.apis import create_student, create_instructor, get_user, list_users

api_routes = [
    ("/students", create_student, ["POST"]),
    ("/instructors", create_instructor, ["POST"]),
    ("/{user_id}", get_user, ["GET"]),
    ("/", list_users, ["GET"]),
]
