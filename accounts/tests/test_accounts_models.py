# accounts/tests/test_models.py
import pytest
from accounts.models import CustomUser


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        assert user.email == "testuser@example.com"
        assert user.check_password("password123")

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        assert user.is_superuser
        assert user.is_staff
