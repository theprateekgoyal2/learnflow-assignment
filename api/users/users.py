from fastapi import APIRouter

from api.users.routes import api_routes

users_router = APIRouter()

for path, endpoint, methods in api_routes:
    users_router.add_api_route(path=path, endpoint=endpoint, methods=methods)
