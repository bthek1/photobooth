# accounts/tests/test_admin.py
import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from accounts.admin import CustomUserAdmin

User = get_user_model()


class TestCustomUserAdmin:
    """Test the custom user admin configuration"""

    def setup_method(self):
        """Set up test dependencies"""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        self.factory = RequestFactory()

    def test_admin_is_registered(self):
        """Test that CustomUser model is registered with CustomUserAdmin"""
        assert admin.site.is_registered(User)
        assert isinstance(admin.site._registry[User], CustomUserAdmin)

    def test_admin_list_display(self):
        """Test the fields displayed in admin list view"""
        expected_list_display = (
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        )
        assert self.admin.list_display == expected_list_display

    def test_admin_list_filter(self):
        """Test the filters available in admin list view"""
        expected_list_filter = ("is_staff", "is_active")
        assert self.admin.list_filter == expected_list_filter

    def test_admin_search_fields(self):
        """Test the searchable fields in admin"""
        expected_search_fields = ("email", "first_name", "last_name")
        assert self.admin.search_fields == expected_search_fields

    def test_admin_ordering(self):
        """Test the default ordering of users in admin"""
        expected_ordering = ("email",)
        assert self.admin.ordering == expected_ordering

    def test_admin_fieldsets_for_existing_user(self):
        """Test fieldsets when editing an existing user"""
        expected_fieldsets = (
            (None, {"fields": ("email", "password")}),
            ("Personal Info", {"fields": ("first_name", "last_name")}),
            (
                "Permissions",
                {
                    "fields": (
                        "is_staff",
                        "is_active",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    ),
                },
            ),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )
        assert self.admin.fieldsets == expected_fieldsets

    def test_admin_add_fieldsets(self):
        """Test fieldsets when adding a new user"""
        expected_add_fieldsets = (
            (
                None,
                {
                    "classes": ("wide",),
                    "fields": (
                        "email",
                        "first_name",
                        "last_name",
                        "password1",
                        "password2",
                        "is_staff",
                        "is_active",
                        "groups",
                    ),
                },
            ),
        )
        assert self.admin.add_fieldsets == expected_add_fieldsets

    @pytest.mark.django_db
    def test_admin_get_form_for_add(self):
        """Test that correct form is used for adding users"""
        request = self.factory.get("/admin/accounts/customuser/add/")
        request.user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )

        form_class = self.admin.get_form(request, obj=None)

        # Should use CustomUserCreationFormAdmin for adding
        from accounts.forms import CustomUserCreationFormAdmin

        assert issubclass(form_class, CustomUserCreationFormAdmin)

    @pytest.mark.django_db
    def test_admin_get_form_for_change(self, user):
        """Test that correct form is used for changing users"""
        request = self.factory.get(f"/admin/accounts/customuser/{user.id}/change/")
        request.user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )

        form_class = self.admin.get_form(request, obj=user)

        # Should use CustomUserChangeForm for editing
        from accounts.forms import CustomUserChangeForm

        assert issubclass(form_class, CustomUserChangeForm)

    @pytest.mark.django_db
    def test_admin_readonly_fields_for_non_superuser(self):
        """Test that readonly fields are configured properly"""
        # Create staff user (not superuser)
        staff_user = User.objects.create_user(
            email="staff@example.com", password="staffpass", is_staff=True
        )

        request = self.factory.get("/admin/accounts/customuser/")
        request.user = staff_user

        readonly_fields = self.admin.get_readonly_fields(request)

        # Check that readonly fields are configured as expected
        expected_readonly = ("last_login", "date_joined", "groups")
        assert readonly_fields == expected_readonly

    @pytest.mark.django_db
    def test_admin_has_add_permission(self):
        """Test add permission logic"""
        # Create superuser
        superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass"
        )

        request = self.factory.get("/admin/accounts/customuser/add/")
        request.user = superuser

        # Superuser should have add permission
        assert self.admin.has_add_permission(request)

    @pytest.mark.django_db
    def test_admin_has_delete_permission(self, user):
        """Test delete permission logic"""
        # Create superuser
        superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass"
        )

        request = self.factory.get(f"/admin/accounts/customuser/{user.id}/delete/")
        request.user = superuser

        # Superuser should have delete permission
        assert self.admin.has_delete_permission(request, user)

    @pytest.mark.django_db
    def test_admin_queryset_optimization(self):
        """Test that admin queryset is properly optimized"""
        request = self.factory.get("/admin/accounts/customuser/")
        request.user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )

        # Create some test users
        User.objects.create_user(email="user1@example.com", password="pass")
        User.objects.create_user(email="user2@example.com", password="pass")

        queryset = self.admin.get_queryset(request)

        # Should return all users
        assert queryset.count() == 3  # 2 test users + 1 admin

        # Should be ordered by email
        emails = list(queryset.values_list("email", flat=True))
        assert emails == sorted(emails)

    def test_admin_filter_horizontal_empty_by_default(self):
        """Test that filter_horizontal is properly configured"""
        # Should be empty tuple by default (no many-to-many fields to show horizontally)
        assert hasattr(self.admin, "filter_horizontal")
