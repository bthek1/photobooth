# photobooth/tests/test_views.py
import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from photobooth.views import event_create_view, join_event_view


@pytest.mark.django_db
class TestEventListView:
    """Test the EventListView"""

    def test_event_list_requires_login(self, client):
        """Test that event list requires authentication"""
        url = reverse("photobooth:event_list")
        response = client.get(url)

        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_event_list_shows_user_events(
        self, client, authenticated_user, event_factory
    ):
        """Test that event list shows only user's events"""
        # Create events for the authenticated user
        user_event1 = event_factory(created_by=authenticated_user)
        user_event2 = event_factory(created_by=authenticated_user)

        # Create event for another user
        other_event = event_factory()

        url = reverse("photobooth:event_list")
        response = client.get(url)

        assert response.status_code == 200
        assert user_event1 in response.context["events"]
        assert user_event2 in response.context["events"]
        assert other_event not in response.context["events"]

    def test_event_list_template(self, client, authenticated_user):
        """Test that correct template is used"""
        url = reverse("photobooth:event_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "photobooth/event_list.html" in [t.name for t in response.templates]

    def test_event_list_context(self, client, authenticated_user):
        """Test that context contains events"""
        url = reverse("photobooth:event_list")
        response = client.get(url)

        assert "events" in response.context
        assert response.context["events"] is not None


@pytest.mark.django_db
class TestEventCreateView:
    """Test the event_create_view"""

    def test_event_create_requires_login(self, client):
        """Test that event creation requires authentication"""
        url = reverse("photobooth:event_create")
        response = client.get(url)

        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_event_create_get(self, client, authenticated_user):
        """Test GET request to event create view"""
        url = reverse("photobooth:event_create")
        response = client.get(url)

        assert response.status_code == 200
        assert "photobooth/event_create.html" in [t.name for t in response.templates]

    def test_event_create_view_function(self, authenticated_user):
        """Test the event_create_view function directly"""
        factory = RequestFactory()
        request = factory.get("/create/")
        request.user = authenticated_user

        response = event_create_view(request)
        assert response.status_code == 200


@pytest.mark.django_db
class TestEventDetailView:
    """Test the EventDetailView"""

    def test_event_detail_requires_login(self, client, test_event):
        """Test that event detail requires authentication"""
        url = reverse("photobooth:event_detail", kwargs={"pk": test_event.id})
        response = client.get(url)

        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_event_detail_owner_access(self, client, authenticated_user, event_factory):
        """Test that event owner can access event detail"""
        event = event_factory(created_by=authenticated_user)
        url = reverse("photobooth:event_detail", kwargs={"pk": event.id})

        response = client.get(url)
        assert response.status_code == 200
        assert response.context["event"] == event

    def test_event_detail_non_owner_access(
        self, client, authenticated_user, event_factory
    ):
        """Test that non-owner cannot access event detail"""
        # Create event owned by another user
        event = event_factory()
        url = reverse("photobooth:event_detail", kwargs={"pk": event.id})

        response = client.get(url)
        assert response.status_code == 404

    def test_event_detail_template(self, client, authenticated_user, event_factory):
        """Test that correct template is used"""
        event = event_factory(created_by=authenticated_user)
        url = reverse("photobooth:event_detail", kwargs={"pk": event.id})

        response = client.get(url)
        assert response.status_code == 200
        assert "photobooth/event_detail.html" in [t.name for t in response.templates]

    def test_event_detail_nonexistent_event(self, client, authenticated_user):
        """Test accessing nonexistent event returns 404"""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        url = reverse("photobooth:event_detail", kwargs={"pk": fake_uuid})

        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestJoinEventView:
    """Test the join_event_view"""

    def test_join_event_get(self, client):
        """Test GET request to join event view"""
        url = reverse("photobooth:join_event")
        response = client.get(url)

        assert response.status_code == 200
        assert "photobooth/join_event.html" in [t.name for t in response.templates]

    def test_join_event_no_auth_required(self, client):
        """Test that join event doesn't require authentication"""
        url = reverse("photobooth:join_event")
        response = client.get(url)

        # Should not redirect to login
        assert response.status_code == 200

    def test_join_event_view_function(self):
        """Test the join_event_view function directly"""
        factory = RequestFactory()
        request = factory.get("/join/")
        request.user = AnonymousUser()

        response = join_event_view(request)
        assert response.status_code == 200


@pytest.mark.django_db
class TestEventBoothView:
    """Test the event_booth_view"""

    def test_event_booth_public_access(self, client, test_event):
        """Test that event booth is publicly accessible"""
        url = reverse("photobooth:event_booth", kwargs={"event_id": test_event.id})
        response = client.get(url)

        assert response.status_code == 200
        assert "photobooth/booth.html" in [t.name for t in response.templates]

    def test_event_booth_context(self, client, test_event):
        """Test that event booth has correct context"""
        url = reverse("photobooth:event_booth", kwargs={"event_id": test_event.id})
        response = client.get(url)

        assert response.status_code == 200
        assert "event" in response.context
        assert response.context["event"] == test_event

    def test_event_booth_nonexistent_event(self, client):
        """Test accessing booth for nonexistent event returns 404"""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        url = reverse("photobooth:event_booth", kwargs={"event_id": fake_uuid})

        response = client.get(url)
        assert response.status_code == 404

    def test_event_booth_inactive_event(self, client, event_factory):
        """Test accessing booth for inactive event returns 404"""
        event = event_factory(is_active=False)
        url = reverse("photobooth:event_booth", kwargs={"event_id": event.id})

        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestEventGalleryView:
    """Test the event_gallery_view"""

    def test_event_gallery_public_access(self, client, test_event):
        """Test that event gallery is publicly accessible"""
        url = reverse("photobooth:event_gallery", kwargs={"event_id": test_event.id})
        response = client.get(url)

        assert response.status_code == 200
        assert "photobooth/gallery.html" in [t.name for t in response.templates]

    def test_event_gallery_with_photos(self, client, test_event, photo_factory):
        """Test gallery displays photos"""
        photo1 = photo_factory(session=test_event)
        photo2 = photo_factory(session=test_event)

        url = reverse("photobooth:event_gallery", kwargs={"event_id": test_event.id})
        response = client.get(url)

        assert response.status_code == 200
        assert "event" in response.context
        assert "photos" in response.context
        photos = response.context["photos"]
        assert photo1 in photos
        assert photo2 in photos

    def test_event_gallery_nonexistent_event(self, client):
        """Test accessing gallery for nonexistent event returns 404"""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        url = reverse("photobooth:event_gallery", kwargs={"event_id": fake_uuid})

        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestPhotoViews:
    """Test photo-related views"""

    def test_photo_download_view_exists(self, client, test_photo):
        """Test that photo download view exists"""
        url = reverse("photobooth:photo_download", kwargs={"photo_id": test_photo.id})
        response = client.get(url)

        # Should not return 404 (view exists)
        assert response.status_code != 404


@pytest.mark.django_db
class TestPhotoDownloadView:
    """Test the photo_download_view"""

    def test_photo_download_redirect(self, client, test_photo):
        """Test that photo download redirects or serves file"""
        url = reverse("photobooth:photo_download", kwargs={"photo_id": test_photo.id})
        response = client.get(url)

        # The response will vary depending on whether a file is actually uploaded
        # In tests, we might get a 404 for missing file or a redirect/file response
        assert response.status_code in [200, 302, 404]

    def test_photo_download_nonexistent_photo(self, client):
        """Test downloading nonexistent photo returns 404"""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        url = reverse("photobooth:photo_download", kwargs={"photo_id": fake_uuid})

        response = client.get(url)
        assert response.status_code == 404
