"""Tests for user creation and retrieval."""

import pytest

from api.users.services.user_service import UserService
from core.exceptions import UserNotFoundError


class TestUserService:

    @pytest.fixture
    def user_service(self, db):
        return UserService(db)

    def test_create_student(self, user_service):
        user = user_service.create_student("Alice", "alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert user.role == "student"
        assert user.id is not None

    def test_create_instructor(self, user_service):
        user = user_service.create_instructor("Bob", "bob@example.com")
        assert user.name == "Bob"
        assert user.role == "instructor"

    def test_get_user_returns_correct_user(self, user_service):
        created = user_service.create_student("Carol", "carol@example.com")
        fetched = user_service.get_user(created.id)
        assert fetched.id == created.id
        assert fetched.name == "Carol"

    def test_get_user_raises_for_nonexistent(self, user_service):
        with pytest.raises(UserNotFoundError):
            user_service.get_user("nonexistent-id")

    def test_list_users_returns_all(self, user_service):
        user_service.create_student("Alice", "alice@example.com")
        user_service.create_instructor("Bob", "bob@example.com")
        users = user_service.list_users()
        assert len(users) == 2

    def test_list_users_empty(self, user_service):
        assert user_service.list_users() == []
