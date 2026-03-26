from fastapi import APIRouter

from api.progress.routes import api_routes

progress_router = APIRouter()

for path, endpoint, methods in api_routes:
    progress_router.add_api_route(path=path, endpoint=endpoint, methods=methods)
