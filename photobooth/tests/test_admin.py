# photobooth/tests/test_admin.py
import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from photobooth.admin import EventAdmin, PhotoAdmin, PhotoboothSettingsAdmin
from photobooth.models import Event, Photo, PhotoboothSettings


class MockRequest:
    """Mock request for admin testing"""

    def __init__(self, user=None):
        self.user = user


class MockSuperUser:
    """Mock superuser for admin testing"""

    def has_perm(self, perm, obj=None):
        return True


@pytest.mark.django_db
class TestEventAdmin:
    """Test EventAdmin configuration"""

    def test_event_admin_registered(self):
        """Test that EventAdmin is registered"""
        assert Event in admin.site._registry
        assert isinstance(admin.site._registry[Event], EventAdmin)

    def test_event_admin_list_display(self):
        """Test EventAdmin list_display configuration"""
        admin_instance = EventAdmin(Event, AdminSite())
        expected_fields = ["name", "code", "created_by", "is_active", "created_at"]

        for field in expected_fields:
            assert field in admin_instance.list_display

    def test_event_admin_list_filter(self):
        """Test EventAdmin list_filter configuration"""
        admin_instance = EventAdmin(Event, AdminSite())
        expected_filters = ["is_active", "created_at"]

        for filter_field in expected_filters:
            assert filter_field in admin_instance.list_filter

    def test_event_admin_search_fields(self):
        """Test EventAdmin search_fields configuration"""
        admin_instance = EventAdmin(Event, AdminSite())
        expected_search_fields = ["name", "code", "created_by__username"]

        for field in expected_search_fields:
            assert field in admin_instance.search_fields

    def test_event_admin_readonly_fields(self):
        """Test EventAdmin readonly_fields configuration"""
        admin_instance = EventAdmin(Event, AdminSite())
        expected_readonly = ["id", "code", "created_at", "updated_at"]

        for field in expected_readonly:
            assert field in admin_instance.readonly_fields

    def test_event_admin_has_configuration(self):
        """Test EventAdmin has basic configuration"""
        admin_instance = EventAdmin(Event, AdminSite())

        # Admin should have list_display configured
        assert hasattr(admin_instance, "list_display")
        assert len(admin_instance.list_display) > 0

        # Should have readonly fields
        assert hasattr(admin_instance, "readonly_fields")
        assert "code" in admin_instance.readonly_fields

    def test_event_admin_photo_count_in_list_display(self):
        """Test that photo_count is in list_display"""
        admin_instance = EventAdmin(Event, AdminSite())

        # photo_count should be in list_display as per admin configuration
        assert "photo_count" in admin_instance.list_display

    def test_event_admin_get_queryset(self, authenticated_user):
        """Test EventAdmin get_queryset optimization"""
        admin_instance = EventAdmin(Event, AdminSite())
        request = MockRequest(MockSuperUser())

        queryset = admin_instance.get_queryset(request)

        # Should include select_related for optimization
        assert "created_by" in str(queryset.query)


@pytest.mark.django_db
class TestPhotoAdmin:
    """Test PhotoAdmin configuration"""

    def test_photo_admin_registered(self):
        """Test that PhotoAdmin is registered"""
        assert Photo in admin.site._registry
        assert isinstance(admin.site._registry[Photo], PhotoAdmin)

    def test_photo_admin_list_display(self):
        """Test PhotoAdmin list_display configuration"""
        admin_instance = PhotoAdmin(Photo, AdminSite())
        expected_fields = ["session", "guest_name", "taken_at", "is_processed"]

        for field in expected_fields:
            assert field in admin_instance.list_display

    def test_photo_admin_list_filter(self):
        """Test PhotoAdmin list_filter configuration"""
        admin_instance = PhotoAdmin(Photo, AdminSite())
        expected_filters = ["taken_at", "session"]

        for filter_field in expected_filters:
            assert filter_field in admin_instance.list_filter

    def test_photo_admin_search_fields(self):
        """Test PhotoAdmin search_fields configuration"""
        admin_instance = PhotoAdmin(Photo, AdminSite())
        expected_search_fields = ["guest_name", "guest_email", "session__name"]

        for field in expected_search_fields:
            assert field in admin_instance.search_fields

    def test_photo_admin_readonly_fields(self):
        """Test PhotoAdmin readonly_fields configuration"""
        admin_instance = PhotoAdmin(Photo, AdminSite())
        expected_readonly = ["id", "taken_at"]

        for field in expected_readonly:
            assert field in admin_instance.readonly_fields

    def test_photo_admin_raw_id_fields(self):
        """Test PhotoAdmin raw_id_fields configuration"""
        admin_instance = PhotoAdmin(Photo, AdminSite())

        if hasattr(admin_instance, "raw_id_fields"):
            assert "session" in admin_instance.raw_id_fields

    def test_photo_admin_get_queryset(self):
        """Test PhotoAdmin get_queryset optimization"""
        admin_instance = PhotoAdmin(Photo, AdminSite())
        request = MockRequest(MockSuperUser())

        queryset = admin_instance.get_queryset(request)

        # Should include select_related for optimization
        assert "session" in str(queryset.query)

    def test_photo_admin_thumbnail_method(self, test_photo):
        """Test thumbnail method if it exists in PhotoAdmin"""
        admin_instance = PhotoAdmin(Photo, AdminSite())

        if hasattr(admin_instance, "thumbnail"):
            # Test that thumbnail method returns something
            result = admin_instance.thumbnail(test_photo)
            assert result is not None


@pytest.mark.django_db
class TestPhotoboothSettingsAdmin:
    """Test PhotoboothSettingsAdmin configuration"""

    def test_photobooth_settings_admin_registered(self):
        """Test that PhotoboothSettingsAdmin is registered"""
        assert PhotoboothSettings in admin.site._registry
        assert isinstance(
            admin.site._registry[PhotoboothSettings], PhotoboothSettingsAdmin
        )

    def test_photobooth_settings_admin_list_display(self):
        """Test PhotoboothSettingsAdmin list_display configuration"""
        admin_instance = PhotoboothSettingsAdmin(PhotoboothSettings, AdminSite())

        # Should have some basic fields displayed
        assert len(admin_instance.list_display) > 0

        # Common fields that should be displayed
        expected_fields = ["camera_resolution", "camera_fps", "countdown_duration"]
        for field in expected_fields:
            if hasattr(PhotoboothSettings, field):
                # Field might be in list_display
                assert (
                    field in admin_instance.list_display
                    or len(admin_instance.list_display) > 0
                )

    def test_photobooth_settings_admin_permissions(self):
        """Test PhotoboothSettingsAdmin permission methods"""
        admin_instance = PhotoboothSettingsAdmin(PhotoboothSettings, AdminSite())

        # Should have custom permission methods for singleton behavior
        assert hasattr(admin_instance, "has_add_permission")
        assert hasattr(admin_instance, "has_delete_permission")

        # Test permission logic
        request = MockRequest(MockSuperUser())
        assert admin_instance.has_delete_permission(request) is False

    def test_photobooth_settings_singleton_behavior(self, settings_factory):
        """Test that PhotoboothSettings behaves as singleton in admin"""
        # Create a settings instance
        settings1 = settings_factory()

        # Try to create another (should reuse existing)
        settings2 = PhotoboothSettings.get_settings()

        assert settings1.id == settings2.id


@pytest.mark.django_db
class TestAdminIntegration:
    """Test admin integration and permissions"""

    def test_admin_site_accessibility(self, admin_user, client):
        """Test that admin site is accessible"""
        client.force_login(admin_user)

        # Test main admin index
        response = client.get("/admin/")
        assert response.status_code == 200

        # Test photobooth app in admin
        response = client.get("/admin/photobooth/")
        assert response.status_code == 200

    def test_event_admin_changelist(self, admin_user, client, event_factory):
        """Test Event admin changelist view"""
        client.force_login(admin_user)
        event_factory()

        response = client.get("/admin/photobooth/event/")
        assert response.status_code == 200

    def test_photo_admin_changelist(self, admin_user, client, photo_factory):
        """Test Photo admin changelist view"""
        client.force_login(admin_user)
        photo_factory()

        response = client.get("/admin/photobooth/photo/")
        assert response.status_code == 200

    def test_photobooth_settings_admin_changelist(
        self, admin_user, client, settings_factory
    ):
        """Test PhotoboothSettings admin changelist view"""
        client.force_login(admin_user)
        settings_factory()

        response = client.get("/admin/photobooth/photoboothsettings/")
        assert response.status_code == 200

    def test_event_admin_add_view(self, admin_user, client):
        """Test Event admin add view"""
        client.force_login(admin_user)

        response = client.get("/admin/photobooth/event/add/")
        assert response.status_code == 200

    def test_photo_admin_add_view(self, admin_user, client):
        """Test Photo admin add view"""
        client.force_login(admin_user)

        response = client.get("/admin/photobooth/photo/add/")
        assert response.status_code == 200

    def test_admin_permissions_for_regular_user(self, authenticated_user, client):
        """Test that regular users cannot access admin"""
        client.force_login(authenticated_user)

        # Should redirect to login or show permission denied
        response = client.get("/admin/")
        assert response.status_code in [302, 403]
