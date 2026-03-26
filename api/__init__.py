from fastapi import APIRouter

from api.users.router import router as users_router
from api.courses.router import router as courses_router
from api.enrollment.router import router as enrollment_router
from api.progress.router import router as progress_router

router = APIRouter()

router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(courses_router, prefix="/courses", tags=["Courses"])
router.include_router(enrollment_router, prefix="/enrollments",tags=["Enrollment"])
router.include_router(progress_router, prefix="/progress", tags=["Progress"])

__all__ = ["router"]
