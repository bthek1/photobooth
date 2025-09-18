# photobooth/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from photobooth.models import Event, Photo, PhotoboothSettings

User = get_user_model()


@pytest.fixture
def user_factory():
    """Factory for creating test users"""

    class UserFactory(DjangoModelFactory):
        class Meta:
            model = User

        email = Faker("email")
        first_name = Faker("first_name")
        last_name = Faker("last_name")

    return UserFactory


@pytest.fixture
def event_factory(user_factory):
    """Factory for creating test events"""

    class EventFactory(DjangoModelFactory):
        class Meta:
            model = Event

        name = Faker("sentence", nb_words=3)
        created_by = SubFactory(user_factory)
        qr_base_url = Faker("url")

    return EventFactory


@pytest.fixture
def photo_factory(event_factory):
    """Factory for creating test photos"""

    class PhotoFactory(DjangoModelFactory):
        class Meta:
            model = Photo

        session = SubFactory(event_factory)
        guest_name = Faker("name")
        guest_email = Faker("email")
        is_processed = False

    return PhotoFactory


@pytest.fixture
def settings_factory():
    """Factory for creating photobooth settings"""

    class SettingsFactory(DjangoModelFactory):
        class Meta:
            model = PhotoboothSettings

        camera_resolution_width = 1920
        camera_resolution_height = 1080
        camera_fps = 30
        photo_quality = 95
        enable_filters = True
        countdown_seconds = 3
        welcome_message = Faker("sentence")
        instructions = Faker("text")
        show_gallery_preview = True
        max_photos_per_session = 1000
        auto_cleanup_days = 30

    return SettingsFactory


@pytest.fixture
def test_user(user_factory):
    """Create a test user instance"""
    return user_factory()


@pytest.fixture
def test_event(event_factory):
    """Create a test event instance"""
    return event_factory()


@pytest.fixture
def test_photo(photo_factory):
    """Create a test photo instance"""
    return photo_factory()


@pytest.fixture
def test_settings(settings_factory):
    """Create a test settings instance"""
    return settings_factory()


@pytest.fixture
def authenticated_user(client, test_user):
    """Create an authenticated user for testing views"""
    client.force_login(test_user)
    return test_user
