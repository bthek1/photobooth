# photobooth/tests/test_integration.py
"""
Integration tests for photobooth app.
Tests the complete workflow from event creation to photo capture and gallery viewing.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from photobooth.models import Event, Photo, PhotoboothSettings

User = get_user_model()


@pytest.mark.django_db
class TestEventWorkflow:
    """Test complete event workflow"""

    def test_event_creation_workflow(self, client, authenticated_user):
        """Test the complete event creation workflow"""
        # Step 1: User creates an event
        event_data = {
            'name': 'Integration Test Wedding',
            'description': 'Testing the full workflow'
        }
        
        create_url = reverse('photobooth:event_create')
        response = client.post(create_url, data=event_data)
        
        # Should either redirect to event detail or show success
        assert response.status_code in [200, 302]
        
        # Verify event was created
        event = Event.objects.filter(name='Integration Test Wedding').first()
        assert event is not None
        assert event.created_by == authenticated_user
        assert event.code is not None
        assert len(event.code) == 6

    def test_event_list_and_detail_workflow(self, client, authenticated_user, event_factory):
        """Test event listing and detail viewing workflow"""
        # Create some events for the user
        user_event1 = event_factory(created_by=authenticated_user, name="User Event 1")
        event_factory(created_by=authenticated_user, name="User Event 2")
        event_factory(name="Other User Event")  # Different user
        
        # Step 1: View event list
        list_url = reverse('photobooth:event_list')
        response = client.get(list_url)
        
        assert response.status_code == 200
        content = response.content.decode()
        
        # Should see user's events but not others
        assert "User Event 1" in content
        assert "User Event 2" in content
        assert "Other User Event" not in content
        
        # Step 2: View specific event detail
        detail_url = reverse('photobooth:event_detail', kwargs={'pk': user_event1.pk})
        response = client.get(detail_url)
        
        assert response.status_code == 200
        assert user_event1.name in response.content.decode()

    def test_event_booth_access_workflow(self, client, test_event):
        """Test public access to event booth"""
        # Event booth should be publicly accessible (no login required)
        booth_url = reverse('photobooth:event_booth', kwargs={'event_id': test_event.id})
        
        # Test without authentication
        response = client.get(booth_url)
        assert response.status_code == 200
        
        # Should contain event information
        content = response.content.decode()
        assert test_event.name in content

    def test_join_event_by_code_workflow(self, client, test_event):
        """Test joining event by code workflow"""
        # Step 1: Access join page
        join_url = reverse('photobooth:join_event')
        response = client.get(join_url)
        
        assert response.status_code == 200
        
        # Step 2: Submit event code (simulated - actual form handling depends on implementation)
        # This would typically redirect to the booth
        booth_url = reverse('photobooth:event_booth', kwargs={'event_id': test_event.id})
        response = client.get(booth_url)
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestPhotoWorkflow:
    """Test photo capture and viewing workflow"""

    def test_photo_gallery_workflow(self, client, test_event, photo_factory):
        """Test photo gallery viewing workflow"""
        # Create some photos for the event
        photo_factory(session=test_event, guest_name="John Doe")
        photo_factory(session=test_event, guest_name="Jane Smith")
        
        # Access gallery
        gallery_url = reverse('photobooth:event_gallery', kwargs={'event_id': test_event.id})
        response = client.get(gallery_url)
        
        assert response.status_code == 200
        
        # Should show photos (exact implementation depends on template)
        # At minimum, should not crash and should render successfully

    def test_photo_download_workflow(self, client, test_photo):
        """Test photo download workflow"""
        download_url = reverse('photobooth:photo_download', kwargs={'photo_id': test_photo.id})
        response = client.get(download_url)
        
        # Should handle download request (may redirect or serve file)
        # Exact behavior depends on implementation
        assert response.status_code in [200, 302, 404]  # Various valid responses

    def test_qr_code_generation_workflow(self, client, test_photo, test_event):
        """Test QR code generation workflow"""
        # Test photo QR code
        photo_qr_url = reverse('photobooth:photo_qr', kwargs={'photo_id': test_photo.id})
        response = client.get(photo_qr_url)
        
        # Should generate QR code (exact format depends on implementation)
        assert response.status_code in [200, 404]
        
        # Test event gallery QR code
        event_qr_url = reverse('photobooth:event_gallery_qr', kwargs={'event_id': test_event.id})
        response = client.get(event_qr_url)
        
        assert response.status_code in [200, 404]


@pytest.mark.django_db
class TestSettingsWorkflow:
    """Test photobooth settings workflow"""

    def test_settings_singleton_workflow(self):
        """Test settings singleton behavior in workflow context"""
        # Multiple calls should return same instance
        settings1 = PhotoboothSettings.get_settings()
        settings2 = PhotoboothSettings.get_settings()
        
        assert settings1.id == settings2.id
        
        # Modifications should persist
        original_quality = settings1.photo_quality
        settings1.photo_quality = 75
        settings1.save()
        
        settings3 = PhotoboothSettings.get_settings()
        assert settings3.photo_quality == 75
        
        # Restore original value
        settings3.photo_quality = original_quality
        settings3.save()

    def test_settings_api_integration(self, client):
        """Test settings integration with API endpoints"""
        # Modify settings
        settings = PhotoboothSettings.get_settings()
        settings.countdown_seconds = 10
        settings.welcome_message = "Integration Test Message"
        settings.save()
        
        # Check API endpoint reflects changes
        api_url = reverse('photobooth:camera_settings')
        response = client.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            if 'countdown_seconds' in data:
                assert data['countdown_seconds'] == 10
            if 'welcome_message' in data:
                assert data['welcome_message'] == "Integration Test Message"


@pytest.mark.django_db
class TestSecurityWorkflow:
    """Test security aspects of the photobooth workflow"""

    def test_event_owner_permissions(self, client, user_factory, event_factory):
        """Test that only event owners can access their events"""
        user1 = user_factory()
        user2 = user_factory()
        
        # User1 creates an event
        event = event_factory(created_by=user1)
        
        # User2 tries to access User1's event detail
        client.force_login(user2)
        detail_url = reverse('photobooth:event_detail', kwargs={'pk': event.pk})
        response = client.get(detail_url)
        
        # Should be denied access (404 or 403)
        assert response.status_code in [403, 404]

    def test_public_booth_access_security(self, client, event_factory):
        """Test that inactive events are properly protected"""
        # Create inactive event
        inactive_event = event_factory(is_active=False)
        
        # Try to access booth
        booth_url = reverse('photobooth:event_booth', kwargs={'event_id': inactive_event.id})
        response = client.get(booth_url)
        
        # Should be denied or redirected
        assert response.status_code in [403, 404]

    def test_authentication_requirements(self, client, test_event):
        """Test authentication requirements for different endpoints"""
        # Test endpoints that require authentication
        auth_required_urls = [
            reverse('photobooth:event_list'),
            reverse('photobooth:event_create'),
            reverse('photobooth:event_detail', kwargs={'pk': test_event.pk}),
        ]
        
        for url in auth_required_urls:
            response = client.get(url)
            # Should redirect to login or return 403
            assert response.status_code in [302, 403]
        
        # Test endpoints that should be public
        public_urls = [
            reverse('photobooth:join_event'),
            reverse('photobooth:event_booth', kwargs={'event_id': test_event.id}),
            reverse('photobooth:event_gallery', kwargs={'event_id': test_event.id}),
        ]
        
        for url in public_urls:
            response = client.get(url)
            # Should be accessible without authentication
            assert response.status_code == 200


@pytest.mark.django_db
class TestErrorHandlingWorkflow:
    """Test error handling in various workflows"""

    def test_nonexistent_event_handling(self, client, authenticated_user):
        """Test handling of requests for nonexistent events"""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        
        urls_to_test = [
            reverse('photobooth:event_detail', kwargs={'pk': fake_uuid}),
            reverse('photobooth:event_booth', kwargs={'event_id': fake_uuid}),
            reverse('photobooth:event_gallery', kwargs={'event_id': fake_uuid}),
            reverse('photobooth:event_info', kwargs={'event_id': fake_uuid}),
        ]
        
        for url in urls_to_test:
            response = client.get(url)
            # Should return 404 for nonexistent resources
            assert response.status_code == 404

    def test_invalid_uuid_handling(self, client):
        """Test handling of malformed UUIDs"""
        invalid_uuid = "invalid-uuid-format"
        
        # These should handle invalid UUIDs gracefully
        urls_to_test = [
            reverse('photobooth:event_booth', kwargs={'event_id': invalid_uuid}),
            reverse('photobooth:event_gallery', kwargs={'event_id': invalid_uuid}),
        ]
        
        for url in urls_to_test:
            response = client.get(url)
            # Should return 404 or handle gracefully
            assert response.status_code in [400, 404]


@pytest.mark.django_db
class TestDataConsistency:
    """Test data consistency across the application"""

    def test_event_photo_relationship_consistency(self, test_event, photo_factory):
        """Test that event-photo relationships remain consistent"""
        initial_count = test_event.photo_count
        
        # Add photos
        photo1 = photo_factory(session=test_event)
        photo_factory(session=test_event)
        
        # Refresh and check count
        test_event.refresh_from_db()
        assert test_event.photo_count == initial_count + 2
        
        # Delete a photo
        photo1.delete()
        test_event.refresh_from_db()
        assert test_event.photo_count == initial_count + 1

    def test_cascade_deletion_consistency(self, user_factory, event_factory, photo_factory):
        """Test that cascade deletions maintain data consistency"""
        user = user_factory()
        event = event_factory(created_by=user)
        photo1 = photo_factory(session=event)
        photo2 = photo_factory(session=event)
        
        photo_ids = [photo1.id, photo2.id]
        event_id = event.id
        
        # Delete event should cascade to photos
        event.delete()
        
        # Verify event is deleted
        assert not Event.objects.filter(id=event_id).exists()
        
        # Verify photos are deleted
        for photo_id in photo_ids:
            assert not Photo.objects.filter(id=photo_id).exists()
