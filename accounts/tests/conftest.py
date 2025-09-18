# accounts/tests/conftest.py
import pytest
from accounts.models import CustomUser



@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="testuser@example.com", password="password123"
    )


