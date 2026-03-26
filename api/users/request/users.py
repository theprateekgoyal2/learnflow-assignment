from __future__ import annotations

from pydantic import BaseModel, EmailStr


class CreateStudentIn(BaseModel):
    name: str
    email: EmailStr


class CreateInstructorIn(BaseModel):
    name: str
    email: EmailStr


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
