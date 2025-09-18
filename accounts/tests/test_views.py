# accounts/tests/test_views.py
import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from accounts.views import ProfileUpdateForm

User = get_user_model()


@pytest.mark.django_db
class TestProfileView:
    """Test the profile view functionality"""

    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        client = Client()
        url = reverse("accounts:profile")
        response = client.get(url)

        # Should redirect to login page
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_profile_view_get_authenticated_user(self, user):
        """Test GET request to profile view for authenticated user"""
        client = Client()
        client.force_login(user)
        url = reverse("accounts:profile")
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert "user" in response.context
        assert response.context["user"] == user
        assert isinstance(response.context["form"], ProfileUpdateForm)

    def test_profile_view_post_valid_data(self, user):
        """Test POST request with valid profile data"""
        client = Client()
        client.force_login(user)
        url = reverse("accounts:profile")

        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }
        response = client.post(url, data)

        # Should redirect after successful update
        assert response.status_code == 302
        assert response.url == reverse("accounts:profile")

        # Check user was updated
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.email == "updated@example.com"

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "profile has been updated successfully" in str(messages[0])

    def test_profile_view_post_invalid_email(self, user):
        """Test POST request with invalid email"""
        client = Client()
        client.force_login(user)
        url = reverse("accounts:profile")

        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "invalid-email",  # Invalid email format
        }
        response = client.post(url, data)

        # Should return form with errors
        assert response.status_code == 200
        assert "form" in response.context
        form = response.context["form"]
        assert form.errors
        assert "email" in form.errors

    def test_profile_view_post_duplicate_email(self, user, user_with_names):
        """Test POST request with email that already exists"""
        client = Client()
        client.force_login(user)
        url = reverse("accounts:profile")

        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": user_with_names.email,  # Email already exists
        }
        response = client.post(url, data)

        # Should return form with errors
        assert response.status_code == 200
        assert "form" in response.context
        form = response.context["form"]
        assert form.errors
        assert "email" in form.errors


@pytest.mark.django_db
class TestProfileUpdateForm:
    """Test the ProfileUpdateForm"""

    def test_form_fields(self):
        """Test that form has correct fields"""
        form = ProfileUpdateForm()
        assert "first_name" in form.fields
        assert "last_name" in form.fields
        assert "email" in form.fields

    def test_form_valid_data(self, user):
        """Test form with valid data"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
        form = ProfileUpdateForm(data=data, instance=user)
        assert form.is_valid()

    def test_form_invalid_email(self, user):
        """Test form with invalid email"""
        data = {"first_name": "John", "last_name": "Doe", "email": "invalid-email"}
        form = ProfileUpdateForm(data=data, instance=user)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_form_missing_email(self, user):
        """Test form with missing required email"""
        data = {"first_name": "John", "last_name": "Doe"}
        form = ProfileUpdateForm(data=data, instance=user)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_form_save_updates_user(self, user):
        """Test that form.save() updates user instance"""
        original_email = user.email
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.com",
        }
        form = ProfileUpdateForm(data=data, instance=user)
        assert form.is_valid()

        updated_user = form.save()
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "User"
        assert updated_user.email == "updated@example.com"
        assert updated_user.email != original_email

    def test_form_widgets_have_css_classes(self):
        """Test that form widgets have proper CSS classes"""
        form = ProfileUpdateForm()

        # Check that widgets have form-control class
        assert "form-control" in form.fields["first_name"].widget.attrs["class"]
        assert "form-control" in form.fields["last_name"].widget.attrs["class"]
        assert "form-control" in form.fields["email"].widget.attrs["class"]

        # Check placeholders
        assert form.fields["first_name"].widget.attrs["placeholder"] == "First Name"
        assert form.fields["last_name"].widget.attrs["placeholder"] == "Last Name"
        assert form.fields["email"].widget.attrs["placeholder"] == "Email Address"
