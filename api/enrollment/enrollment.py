from fastapi import APIRouter

from api.enrollment.routes import api_routes

enrollment_router = APIRouter()

for path, endpoint, methods in api_routes:
    enrollment_router.add_api_route(path=path, endpoint=endpoint, methods=methods)
