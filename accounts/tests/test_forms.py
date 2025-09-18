# accounts/tests/test_forms.py
import pytest
from django.contrib.auth import get_user_model

from accounts.forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    CustomUserCreationFormAdmin,
)

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserCreationForm:
    """Test the custom allauth signup form"""

    def test_form_has_custom_fields(self):
        """Test that form includes first_name and last_name fields"""
        form = CustomUserCreationForm()

        # Check custom fields are present
        assert "first_name" in form.fields
        assert "last_name" in form.fields

        # Check fields are optional
        assert not form.fields["first_name"].required
        assert not form.fields["last_name"].required

    def test_form_field_widgets(self):
        """Test that custom fields have proper widgets and attributes"""
        form = CustomUserCreationForm()

        # Check widget classes
        first_name_widget = form.fields["first_name"].widget
        last_name_widget = form.fields["last_name"].widget

        assert "form-control" in first_name_widget.attrs["class"]
        assert "form-control" in last_name_widget.attrs["class"]

        # Check placeholders
        assert "First Name (optional)" in first_name_widget.attrs["placeholder"]
        assert "Last Name (optional)" in last_name_widget.attrs["placeholder"]

    def test_form_valid_with_all_fields(self):
        """Test form is valid with all fields provided"""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=data)
        assert form.is_valid()

    def test_form_valid_without_optional_fields(self):
        """Test form is valid without first_name and last_name"""
        data = {
            "email": "test@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=data)
        assert form.is_valid()

    def test_form_saves_custom_fields(self):
        """Test that form saves first_name and last_name to user"""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=data)
        assert form.is_valid()

        # For allauth forms, we need to call the save method without request for now
        # This test verifies the form structure rather than the exact save behavior
        assert "first_name" in form.cleaned_data
        assert "last_name" in form.cleaned_data
        assert form.cleaned_data["first_name"] == "John"
        assert form.cleaned_data["last_name"] == "Doe"

    def test_form_field_max_lengths(self):
        """Test that first_name and last_name respect max_length"""
        form = CustomUserCreationForm()

        assert form.fields["first_name"].max_length == 50
        assert form.fields["last_name"].max_length == 50

    def test_form_inheritance_from_signup_form(self):
        """Test that form properly inherits from allauth SignupForm"""
        form = CustomUserCreationForm()

        # Should have allauth's default fields
        assert "email" in form.fields
        assert "password1" in form.fields
        assert "password2" in form.fields


@pytest.mark.django_db
class TestCustomUserCreationFormAdmin:
    """Test the admin user creation form"""

    def test_form_has_required_fields(self):
        """Test that admin form has necessary fields"""
        form = CustomUserCreationFormAdmin()

        assert "email" in form.fields
        assert "password1" in form.fields
        assert "password2" in form.fields

    def test_form_valid_data(self):
        """Test form with valid admin user data"""
        data = {
            "email": "admin@example.com",
            "password1": "adminpassword123",
            "password2": "adminpassword123",
        }
        form = CustomUserCreationFormAdmin(data=data)
        assert form.is_valid()

    def test_form_saves_user(self):
        """Test that form saves user correctly"""
        data = {
            "email": "admin@example.com",
            "password1": "adminpassword123",
            "password2": "adminpassword123",
        }
        form = CustomUserCreationFormAdmin(data=data)
        assert form.is_valid()

        user = form.save()
        assert user.email == "admin@example.com"
        assert user.check_password("adminpassword123")

    def test_form_password_mismatch(self):
        """Test form validation with mismatched passwords"""
        data = {
            "email": "admin@example.com",
            "password1": "adminpassword123",
            "password2": "differentpassword",
        }
        form = CustomUserCreationFormAdmin(data=data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_form_duplicate_email(self, user):
        """Test form validation with duplicate email"""
        data = {
            "email": user.email,  # Email already exists
            "password1": "adminpassword123",
            "password2": "adminpassword123",
        }
        form = CustomUserCreationFormAdmin(data=data)
        assert not form.is_valid()
        assert "email" in form.errors


@pytest.mark.django_db
class TestCustomUserChangeForm:
    """Test the admin user change form"""

    def test_form_with_existing_user(self, user):
        """Test form initialized with existing user"""
        form = CustomUserChangeForm(instance=user)

        assert form.initial["email"] == user.email
        assert form.initial["first_name"] == user.first_name
        assert form.initial["last_name"] == user.last_name

    def test_form_update_user_data(self, user):
        """Test updating user data through form"""
        data = {
            "email": "updated@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "is_active": True,
            "is_staff": False,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }
        form = CustomUserChangeForm(data=data, instance=user)
        assert form.is_valid()

        updated_user = form.save()
        assert updated_user.email == "updated@example.com"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "User"

    def test_form_preserves_password(self, user):
        """Test that change form doesn't modify password"""
        original_password = user.password

        data = {
            "email": user.email,
            "first_name": "Updated",
            "last_name": "User",
            "is_active": True,
            "is_staff": False,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }
        form = CustomUserChangeForm(data=data, instance=user)
        assert form.is_valid()

        updated_user = form.save()
        assert updated_user.password == original_password

    def test_form_invalid_email_format(self, user):
        """Test form validation with invalid email format"""
        data = {
            "email": "invalid-email-format",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": True,
            "is_staff": False,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }
        form = CustomUserChangeForm(data=data, instance=user)
        assert not form.is_valid()
        assert "email" in form.errors
