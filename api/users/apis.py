from fastapi import Depends
from sqlalchemy.orm import Session

from api.users.request.users import CreateInstructorIn, CreateStudentIn, UserOut
from api.users.services.user_service import UserService
from core.db import get_db


async def create_student(payload: CreateStudentIn, db: Session = Depends(get_db)) -> UserOut:
    user = UserService(db).create_student(payload.name, payload.email)
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


async def create_instructor(payload: CreateInstructorIn, db: Session = Depends(get_db)) -> UserOut:
    user = UserService(db).create_instructor(payload.name, payload.email)
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


async def get_user(user_id: str, db: Session = Depends(get_db)) -> UserOut:
    user = UserService(db).get_user(user_id)
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


async def list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    return [UserOut(id=u.id, name=u.name, email=u.email, role=u.role) for u in UserService(db).list_users()]