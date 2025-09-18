# accounts/tests/conftest.py
import pytest

from accounts.models import CustomUser


@pytest.fixture
def user():
    """Create a basic test user"""
    return CustomUser.objects.create_user(
        email="testuser@example.com", password="password123"
    )


@pytest.fixture
def user_with_names():
    """Create a test user with first and last names"""
    return CustomUser.objects.create_user(
        email="john.doe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def superuser():
    """Create a test superuser"""
    return CustomUser.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def inactive_user():
    """Create an inactive test user"""
    user = CustomUser.objects.create_user(
        email="inactive@example.com", password="password123"
    )
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def multiple_users():
    """Create multiple test users for testing queries"""
    users = []
    for i in range(3):
        user = CustomUser.objects.create_user(
            email=f"user{i}@example.com",
            password="password123",
            first_name=f"User{i}",
            last_name="Test",
        )
        users.append(user)
    return users
    return users
