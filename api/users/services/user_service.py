from uuid import uuid4

from sqlalchemy.orm import Session

from api.users.models.users import UserTable
from core.exceptions import UserNotFoundError


class UserService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_student(self, name: str, email: str) -> UserTable:
        user = UserTable(id=str(uuid4()), name=name, email=email, role="student")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_instructor(self, name: str, email: str) -> UserTable:
        user = UserTable(id=str(uuid4()), name=name, email=email, role="instructor")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: str) -> UserTable:
        user = self.db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def list_users(self) -> list[UserTable]:
        return self.db.query(UserTable).all()
