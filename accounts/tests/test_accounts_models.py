# accounts/tests/test_models.py
from datetime import UTC, datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from accounts.models import CustomUser, CustomUserManager, get_utc_now


@pytest.mark.django_db
class TestCustomUserManager:
    """Test the CustomUserManager functionality"""

    def test_create_user_with_email_and_password(self):
        """Test creating a user with email and password"""
        user = CustomUser.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        assert user.email == "testuser@example.com"
        assert user.check_password("password123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.date_joined is not None

    def test_create_user_with_extra_fields(self):
        """Test creating a user with additional fields"""
        user = CustomUser.objects.create_user(
            email="john.doe@example.com",
            password="securepass",
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "john.doe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.check_password("securepass")

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError"""
        with pytest.raises(ValueError, match="The Email field must be set"):
            CustomUser.objects.create_user(email="", password="password123")

    def test_create_user_with_none_email_raises_error(self):
        """Test that creating a user with None email raises ValueError"""
        with pytest.raises(ValueError, match="The Email field must be set"):
            CustomUser.objects.create_user(email=None, password="password123")

    def test_create_user_email_normalization(self):
        """Test that email is normalized during user creation"""
        user = CustomUser.objects.create_user(
            email="TestUser@EXAMPLE.COM", password="password123"
        )
        assert user.email == "TestUser@example.com"  # Domain should be lowercase

    def test_create_superuser_with_defaults(self):
        """Test creating a superuser with default staff/superuser flags"""
        user = CustomUser.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        assert user.email == "admin@example.com"
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.check_password("adminpass")

    def test_create_superuser_with_extra_fields(self):
        """Test creating a superuser with additional fields"""
        user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
        )
        assert user.first_name == "Admin"
        assert user.last_name == "User"
        assert user.is_superuser is True
        assert user.is_staff is True


@pytest.mark.django_db
class TestCustomUserModel:
    """Test the CustomUser model functionality"""

    def test_user_string_representation(self):
        """Test the string representation of user returns email"""
        user = CustomUser.objects.create_user(
            email="test@example.com", password="password123"
        )
        assert str(user) == "test@example.com"

    def test_user_email_uniqueness(self):
        """Test that email field enforces uniqueness"""
        CustomUser.objects.create_user(
            email="unique@example.com", password="password123"
        )

        # Attempting to create another user with same email should fail
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                email="unique@example.com", password="anotherpassword"
            )

    def test_user_default_field_values(self):
        """Test default values for user fields"""
        user = CustomUser.objects.create_user(
            email="defaults@example.com", password="password123"
        )
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        # first_name and last_name are nullable fields, so they default to None
        assert user.first_name is None or user.first_name == ""
        assert user.last_name is None or user.last_name == ""
        assert user.date_joined is not None

        # Check that date_joined is close to now (within 1 second)
        now = datetime.now(UTC)
        time_diff = abs((now - user.date_joined).total_seconds())
        assert time_diff < 1.0

    def test_user_optional_fields_can_be_none(self):
        """Test that optional fields can be None"""
        user = CustomUser(email="optional@example.com", first_name=None, last_name=None)
        user.set_password("password123")
        user.save()

        assert user.first_name is None
        assert user.last_name is None

    def test_user_optional_fields_can_be_blank(self):
        """Test that optional fields can be blank strings"""
        user = CustomUser.objects.create_user(
            email="blank@example.com",
            password="password123",
            first_name="",
            last_name="",
        )
        assert user.first_name == ""
        assert user.last_name == ""

    def test_user_first_and_last_name_max_length(self):
        """Test maximum length constraints on name fields"""
        long_name = "a" * 51  # Exceeds max_length of 50

        user = CustomUser(
            email="longname@example.com", first_name=long_name, last_name=long_name
        )

        with pytest.raises(ValidationError):
            user.full_clean()

    def test_user_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email"""
        assert CustomUser.USERNAME_FIELD == "email"

    def test_user_required_fields_empty(self):
        """Test that REQUIRED_FIELDS is empty (only email required)"""
        assert CustomUser.REQUIRED_FIELDS == []

    def test_user_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = CustomUser.objects.create_user(
            email="hash@example.com", password="plainpassword"
        )
        # Password should be hashed, not stored in plain text
        assert user.password != "plainpassword"
        # In test settings we use MD5 for speed, in production it would be pbkdf2_sha256
        assert user.password.startswith(("pbkdf2_sha256$", "bcrypt$", "argon2", "md5$"))

        # But check_password should work
        assert user.check_password("plainpassword") is True
        assert user.check_password("wrongpassword") is False

    def test_user_inactive_user(self):
        """Test creating and working with inactive users"""
        user = CustomUser.objects.create_user(
            email="inactive@example.com", password="password123"
        )
        user.is_active = False
        user.save()

        assert user.is_active is False
        # User should still be able to authenticate but be marked inactive
        assert user.check_password("password123") is True

    def test_user_manager_attached_to_model(self):
        """Test that CustomUserManager is properly attached"""
        assert isinstance(CustomUser.objects, CustomUserManager)

    def test_user_permissions_mixin_integration(self):
        """Test that PermissionsMixin functionality is available"""
        user = CustomUser.objects.create_user(
            email="perms@example.com", password="password123"
        )

        # These methods should be available from PermissionsMixin
        assert hasattr(user, "get_user_permissions")
        assert hasattr(user, "get_group_permissions")
        assert hasattr(user, "has_perm")
        assert hasattr(user, "has_perms")
        assert hasattr(user, "has_module_perms")


@pytest.mark.django_db
class TestGetUtcNow:
    """Test the get_utc_now utility function"""

    def test_get_utc_now_returns_datetime_with_utc_timezone(self):
        """Test that get_utc_now returns a UTC datetime"""
        result = get_utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC

    def test_get_utc_now_is_close_to_current_time(self):
        """Test that get_utc_now returns current time"""
        before = datetime.now(UTC)
        result = get_utc_now()
        after = datetime.now(UTC)

        assert before <= result <= after

    def test_user_date_joined_uses_get_utc_now(self):
        """Test that date_joined field uses get_utc_now as default"""
        user = CustomUser.objects.create_user(
            email="timezone@example.com", password="password123"
        )

        # date_joined should have UTC timezone
        assert user.date_joined.tzinfo == UTC
        # date_joined should have UTC timezone
        assert user.date_joined.tzinfo == UTC
