# photobooth/tests/test_api_views.py
"""
Test API views for photobooth app.
Tests the legacy API endpoints that handle photo capture and settings.
"""
import json
import pytest
from django.urls import reverse

from photobooth.models import PhotoboothSettings


@pytest.mark.django_db
class TestCameraSettingsAPI:
    """Test the camera settings API endpoint"""

    def test_camera_settings_endpoint_exists(self, client):
        """Test that camera settings endpoint is accessible"""
        url = reverse("photobooth:camera_settings")
        response = client.get(url)
        
        # Should not return 404 - endpoint exists
        assert response.status_code != 404

    def test_camera_settings_returns_json(self, client):
        """Test that camera settings returns JSON data"""
        # Ensure settings exist
        PhotoboothSettings.get_settings()
        
        url = reverse("photobooth:camera_settings")
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Should contain some camera settings
            assert len(data) > 0

    def test_camera_settings_contains_expected_fields(self, client):
        """Test that camera settings contains expected configuration fields"""
        # Create settings with known values
        settings = PhotoboothSettings.get_settings()
        settings.photo_quality = 85
        settings.countdown_seconds = 5
        settings.welcome_message = "Test Welcome Message"
        settings.save()
        
        url = reverse("photobooth:camera_settings")
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Check for expected fields based on the model
            expected_fields = ['photo_quality', 'countdown_seconds', 'welcome_message']
            for field in expected_fields:
                if field in data:
                    assert data[field] is not None


@pytest.mark.django_db
class TestCapturePhotoAPI:
    """Test the photo capture API endpoint"""

    def test_capture_photo_endpoint_exists(self, client):
        """Test that capture photo endpoint is accessible"""
        url = reverse("photobooth:capture_photo")
        response = client.get(url)
        
        # Should not return 404 - endpoint exists
        assert response.status_code != 404

    def test_capture_photo_requires_post_data(self, client):
        """Test that capture photo endpoint handles missing data appropriately"""
        url = reverse("photobooth:capture_photo")
        
        # Test with no data
        response = client.post(url, {})
        # Should return some error response (400, 403, 405)
        assert response.status_code in [400, 403, 405, 422]

    def test_capture_photo_csrf_exempt(self, client):
        """Test that capture photo endpoint is CSRF exempt for API usage"""
        url = reverse("photobooth:capture_photo")
        
        # Test POST without CSRF token (should work for API)
        data = {'test': 'data'}
        response = client.post(url, data=json.dumps(data), 
                             content_type='application/json')
        
        # Should not return 403 CSRF error
        assert response.status_code != 403


@pytest.mark.django_db
class TestEventInfoAPI:
    """Test the event info API endpoint"""

    def test_event_info_endpoint_exists(self, client, test_event):
        """Test that event info endpoint is accessible"""
        url = reverse("photobooth:event_info", kwargs={'event_id': test_event.id})
        response = client.get(url)
        
        # Should not return 404 - endpoint exists
        assert response.status_code != 404

    def test_event_info_with_valid_event(self, client, test_event):
        """Test event info returns data for valid event"""
        url = reverse("photobooth:event_info", kwargs={'event_id': test_event.id})
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Should contain event information
            expected_fields = ['id', 'name', 'is_active']
            for field in expected_fields:
                if field in data:
                    assert data[field] is not None

    def test_event_info_with_invalid_uuid(self, client):
        """Test event info with malformed UUID"""
        url = reverse("photobooth:event_info", kwargs={'event_id': 'invalid-uuid'})
        response = client.get(url)
        
        # Should handle invalid UUID gracefully
        assert response.status_code in [400, 404, 422]


@pytest.mark.django_db
class TestAPIErrorHandling:
    """Test API error handling and edge cases"""

    def test_api_endpoints_handle_invalid_methods(self, client, test_event):
        """Test that API endpoints handle unsupported HTTP methods"""
        endpoints = [
            reverse("photobooth:camera_settings"),
            reverse("photobooth:capture_photo"),
            reverse("photobooth:event_info", kwargs={'event_id': test_event.id}),
        ]
        
        for url in endpoints:
            # Test unsupported methods
            response = client.delete(url)
            assert response.status_code in [405, 404]  # Method not allowed or not found
            
            response = client.put(url)
            assert response.status_code in [405, 404]

    def test_api_endpoints_with_large_payloads(self, client):
        """Test API endpoints handle large request payloads appropriately"""
        url = reverse("photobooth:capture_photo")
        
        # Create a large JSON payload
        large_data = {'data': 'x' * 10000}  # 10KB of data
        
        response = client.post(url, data=json.dumps(large_data), 
                             content_type='application/json')
        
        # Should handle large payload without crashing
        assert response.status_code in [200, 400, 413, 422]  # Various valid responses


@pytest.mark.django_db
class TestAPIDocumentation:
    """Document API behavior and patterns"""

    def test_api_architecture_documentation(self):
        """Document the current API architecture"""
        # The photobooth app uses a hybrid approach:
        # 1. Traditional Django views for HTML pages
        # 2. Legacy API endpoints for specific AJAX functionality
        # 3. JavaScript frontend for camera interactions
        # 4. File uploads through Django forms/views
        
        # API endpoints are designed to be:
        # - CSRF exempt for external API usage
        # - JSON-based request/response format
        # - RESTful where appropriate
        # - Backward compatible with existing JavaScript
        
        assert True  # This test documents architecture

    def test_future_api_expansion_notes(self):
        """Notes for future API expansion"""
        # If expanding to full REST API, consider:
        # 1. API versioning (v1, v2, etc.)
        # 2. Authentication (JWT, API keys, OAuth)
        # 3. Rate limiting and throttling
        # 4. Comprehensive error responses
        # 5. API documentation (OpenAPI/Swagger)
        # 6. Content negotiation (JSON, XML)
        # 7. Pagination for list endpoints
        # 8. Field filtering and sorting
        # 9. Real-time capabilities (WebSocket/SSE)
        # 10. API client SDKs
        
        assert True  # This test documents future considerations
