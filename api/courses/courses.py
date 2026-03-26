from fastapi import APIRouter

from api.courses.routes import api_routes

courses_router = APIRouter()

for path, endpoint, methods in api_routes:
    courses_router.add_api_route(path=path, endpoint=endpoint, methods=methods)
