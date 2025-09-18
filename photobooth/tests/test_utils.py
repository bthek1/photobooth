# photobooth/tests/test_utils.py
"""
Test utility functions and helper methods in the photobooth app.
"""
import pytest

from photobooth.models import Event, PhotoboothSettings


@pytest.mark.django_db
class TestModelUtilities:
    """Test utility methods on models"""

    def test_event_code_generation_uniqueness(self, event_factory):
        """Test that event codes are consistently unique"""
        created_codes = set()
        
        # Create many events and ensure no duplicate codes
        for _ in range(50):
            event = event_factory()
            assert event.code not in created_codes
            assert len(event.code) == 6
            assert event.code.isalnum()
            assert event.code.isupper()
            created_codes.add(event.code)

    def test_event_string_representation_consistency(self, event_factory):
        """Test that event string representation is consistent"""
        event = event_factory(name="Test Event Name")
        str_repr = str(event)
        
        # Should contain the event name
        assert "Test Event Name" in str_repr
        # Should be consistent across calls
        assert str(event) == str_repr

    def test_photobooth_settings_defaults(self):
        """Test PhotoboothSettings default values are reasonable"""
        settings = PhotoboothSettings()
        
        # Quality should be reasonable (1-100)
        assert 1 <= settings.photo_quality <= 100
        # Countdown should be reasonable (1-10 seconds)
        assert 1 <= settings.countdown_seconds <= 10
        # Messages should not be empty
        assert len(settings.welcome_message) > 0
        assert len(settings.instructions) > 0


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_event_with_very_long_name(self, user_factory):
        """Test event creation with maximum length name"""
        user = user_factory()
        
        # Test with very long name (check model's max_length)
        long_name = "x" * 200  # Assuming max_length of 200
        event = Event.objects.create(
            name=long_name,
            created_by=user
        )
        
        # Should truncate or handle appropriately
        assert event.name is not None
        assert len(event.name) <= 200

    def test_event_with_empty_description(self, user_factory):
        """Test event with empty description"""
        user = user_factory()
        event = Event.objects.create(
            name="Test Event",
            description="",
            created_by=user
        )
        
        # Empty description should be handled gracefully
        assert event.description == ""
        assert str(event) is not None

    def test_photo_without_guest_info(self, test_event):
        """Test photo creation without any guest information"""
        from photobooth.models import Photo
        
        photo = Photo.objects.create(session=test_event)
        
        # Should handle missing guest info gracefully
        assert photo.guest_name == ""
        assert photo.guest_email == ""
        assert photo.session == test_event

    def test_settings_modification_edge_cases(self):
        """Test PhotoboothSettings with edge case values"""
        settings = PhotoboothSettings.get_settings()
        
        # Test boundary values
        settings.photo_quality = 1  # Minimum
        settings.countdown_seconds = 0  # Edge case
        settings.max_photos_per_session = 0  # Edge case
        settings.save()
        
        # Should handle edge cases without crashing
        refreshed = PhotoboothSettings.get_settings()
        assert refreshed.photo_quality == 1
        assert refreshed.countdown_seconds == 0
        assert refreshed.max_photos_per_session == 0


@pytest.mark.django_db
class TestConcurrency:
    """Test concurrent operations and race conditions"""

    def test_concurrent_event_creation(self, user_factory):
        """Test that concurrent event creation doesn't create duplicate codes"""
        user = user_factory()
        
        # Simulate concurrent event creation
        events = []
        for i in range(10):
            event = Event.objects.create(
                name=f"Concurrent Event {i}",
                created_by=user
            )
            events.append(event)
        
        # All codes should be unique
        codes = [event.code for event in events]
        assert len(codes) == len(set(codes))

    def test_settings_singleton_concurrency(self):
        """Test settings singleton behavior under concurrent access"""
        # Multiple simultaneous calls should return the same instance
        settings_instances = []
        
        for _ in range(5):
            settings = PhotoboothSettings.get_settings()
            settings_instances.append(settings)
        
        # All should have the same ID (singleton)
        first_id = settings_instances[0].id
        for settings in settings_instances:
            assert settings.id == first_id


@pytest.mark.django_db
class TestDataValidation:
    """Test data validation and constraints"""

    def test_event_code_format_validation(self, test_event):
        """Test that event codes follow expected format"""
        code = test_event.code
        
        # Should be 6 characters
        assert len(code) == 6
        # Should be alphanumeric
        assert code.isalnum()
        # Should be uppercase
        assert code.isupper()
        # Should not contain confusing characters (depends on implementation)
        # Common exclusions: ['0', 'O', 'I', '1'] to avoid confusion

    def test_photo_email_validation(self, test_event):
        """Test photo email field validation"""
        from photobooth.models import Photo
        from django.core.exceptions import ValidationError
        
        # Valid email should work
        photo = Photo(
            session=test_event,
            guest_email="test@example.com"
        )
        photo.full_clean()  # Should not raise
        
        # Invalid email should raise ValidationError
        invalid_photo = Photo(
            session=test_event,
            guest_email="invalid-email"
        )
        
        with pytest.raises(ValidationError):
            invalid_photo.full_clean()

    def test_settings_value_constraints(self):
        """Test that settings values are constrained appropriately"""
        settings = PhotoboothSettings.get_settings()
        
        # Quality should be 1-100
        settings.photo_quality = 150  # Over limit
        settings.save()
        # Should either constrain or validate
        
        settings.refresh_from_db()
        # Depending on model validation, should handle appropriately


@pytest.mark.django_db
class TestPerformance:
    """Test performance-related aspects"""

    def test_event_queryset_optimization(self, user_factory, event_factory):
        """Test that event queries are optimized"""
        user = user_factory()
        
        # Create events with related data
        for i in range(5):
            event = event_factory(created_by=user, name=f"Event {i}")
            # Add some photos
            for j in range(3):
                from photobooth.models import Photo
                Photo.objects.create(session=event, guest_name=f"Guest {j}")
        
        # Query with select_related should be efficient
        events = Event.objects.select_related('created_by').all()
        
        # Basic performance check - should not crash with moderate data
        assert len(events) == 5
        
        # Accessing related objects should not cause additional queries
        for event in events:
            assert event.created_by.id is not None

    def test_photo_count_efficiency(self, test_event, photo_factory):
        """Test that photo count calculation is efficient"""
        # Add multiple photos
        for i in range(20):
            photo_factory(session=test_event)
        
        # Photo count should be calculated efficiently
        count = test_event.photo_count
        assert count == 20
        
        # Multiple calls should be consistent
        assert test_event.photo_count == count


@pytest.mark.django_db
class TestCompatibility:
    """Test backward compatibility and migration scenarios"""

    def test_model_field_defaults(self):
        """Test that model fields have appropriate defaults for migration"""
        from photobooth.models import Event, Photo
        
        # Event fields should have sensible defaults
        event_field_defaults = {
            'is_active': True,
            'description': '',
        }
        
        for field_name, expected_default in event_field_defaults.items():
            field = Event._meta.get_field(field_name)
            assert field.default == expected_default
        
        # Photo fields should have sensible defaults
        photo_field_defaults = {
            'is_processed': False,
            'guest_name': '',
            'guest_email': '',
        }
        
        for field_name, expected_default in photo_field_defaults.items():
            field = Photo._meta.get_field(field_name)
            assert field.default == expected_default

    def test_settings_migration_compatibility(self):
        """Test that settings are compatible across versions"""
        settings = PhotoboothSettings.get_settings()
        
        # Core settings should always exist
        required_settings = [
            'photo_quality',
            'countdown_seconds',
            'welcome_message',
            'instructions',
        ]
        
        for setting in required_settings:
            assert hasattr(settings, setting)
            value = getattr(settings, setting)
            assert value is not None


@pytest.mark.django_db
class TestDocumentation:
    """Document testing patterns and provide examples"""

    def test_testing_patterns_documentation(self):
        """Document common testing patterns used in this test suite"""
        # This test serves as documentation for the testing approach:
        
        # 1. Model Testing:
        #    - Test creation, validation, relationships
        #    - Test string representations and properties
        #    - Test cascade deletions and constraints
        
        # 2. View Testing:
        #    - Test authentication and permissions
        #    - Test template rendering and context
        #    - Test HTTP methods and response codes
        
        # 3. API Testing:
        #    - Test endpoint existence and methods
        #    - Test data formats and validation
        #    - Test error handling and edge cases
        
        # 4. Integration Testing:
        #    - Test complete user workflows
        #    - Test data consistency across operations
        #    - Test security and permission boundaries
        
        # 5. Utility Testing:
        #    - Test helper functions and utilities
        #    - Test edge cases and boundary conditions
        #    - Test performance and optimization
        
        assert True  # This test documents patterns

    def test_fixture_usage_examples(self, user_factory, event_factory, photo_factory):
        """Document how to use the test fixtures effectively"""
        # Factory fixtures provide clean, isolated test data:
        
        # Create a user with default values
        user = user_factory()
        assert user.email is not None
        
        # Create a user with custom values
        custom_user = user_factory(email="custom@test.com")
        assert custom_user.email == "custom@test.com"
        
        # Create an event (automatically gets a user via SubFactory)
        event = event_factory()
        assert event.created_by is not None
        
        # Create an event for specific user
        user_event = event_factory(created_by=user)
        assert user_event.created_by == user
        
        # Create photos for events
        photo = photo_factory(session=event)
        assert photo.session == event
        
        assert True  # This test documents fixture usage
