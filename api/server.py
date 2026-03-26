"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import router
from core.exceptions import (
    AlreadyEnrolledError,
    CourseHasActiveStudentsError,
    CourseNotFoundError,
    LearnFlowError,
    LessonNotFoundError,
    NotEnrolledError,
    PermissionDeniedError,
    UserNotFoundError,
)

_STATUS_MAP: dict[type[LearnFlowError], int] = {
    UserNotFoundError: 404,
    CourseNotFoundError: 404,
    LessonNotFoundError: 404,
    NotEnrolledError: 403,
    PermissionDeniedError: 403,
    AlreadyEnrolledError: 409,
    CourseHasActiveStudentsError: 409,
}


def init_routers(app: FastAPI) -> None:
    app.include_router(router)


def init_listeners(app: FastAPI) -> None:
    for exc_class, status_code in _STATUS_MAP.items():
        def _make_handler(code: int):
            async def handler(request: Request, exc: LearnFlowError) -> JSONResponse:
                return JSONResponse(status_code=code, content={"detail": str(exc)})
            return handler
        app.add_exception_handler(exc_class, _make_handler(status_code))


def create_app() -> FastAPI:
    app = FastAPI(
        title="LearnFlow LMS API",
        description="Core backend for the LearnFlow Learning Management System.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_routers(app)
    init_listeners(app)

    @app.on_event("startup")
    def startup() -> None:
        # Import all ORM models so SQLAlchemy registers them before create_all()
        import api.users.models.users          # noqa: F401
        import api.courses.models.courses      # noqa: F401
        import api.enrollment.models.enrollment  # noqa: F401

        from core.db import Base, engine
        Base.metadata.create_all(bind=engine)
        print("[INFO] LearnFlow LMS started — tables ready.")

    @app.on_event("shutdown")
    def shutdown() -> None:
        print("[INFO] LearnFlow LMS shutting down.")

    @app.get("/", tags=["Health"])
    def health_check():
        return {"status": "ok", "service": "LearnFlow LMS"}

    return app


app = create_app()
