import os
import secrets
import string
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone


def photo_upload_path(instance, filename):
    """Generate upload path for photos based on session and timestamp"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("photos", str(instance.session.id), filename)


def generate_event_code():
    """Generate a random 6-character code for events"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(characters) for _ in range(6))
        # Ensure the code is unique
        if not Event.objects.filter(code=code).exists():
            return code


class Event(models.Model):
    """
    Represents an event (e.g., wedding, party) for photobooth sessions
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=200, help_text="Event name (e.g., 'John & Jane Wedding')"
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        default=generate_event_code,
        help_text="Easy random code for joining the event",
    )
    date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(
        default=True, help_text="Whether this event is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="events",
        help_text="User who created the event",
    )
    qr_base_url = models.URLField(
        blank=True, help_text="Base URL for QR codes (e.g., your domain)"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_absolute_url(self):
        return reverse("photobooth:event_gallery", kwargs={"event_id": self.id})

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    """
    Represents a single photo taken in the photobooth, linked to an event
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=photo_upload_path)
    thumbnail = models.ImageField(upload_to=photo_upload_path, blank=True, null=True)

    # Metadata
    taken_at = models.DateTimeField(auto_now_add=True)
    guest_name = models.CharField(
        max_length=200, blank=True, help_text="Optional guest name"
    )
    guest_email = models.EmailField(
        blank=True, help_text="Optional email for photo delivery"
    )

    # Photo processing
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-taken_at"]

    def __str__(self):
        return f"Photo {self.id} - {self.session.name}"

    def get_absolute_url(self):
        return reverse("photobooth:photo_detail", kwargs={"photo_id": self.id})

    @property
    def download_url(self):
        return reverse("photobooth:photo_download", kwargs={"photo_id": self.id})


class PhotoboothSettings(models.Model):
    """
    Global settings for the photobooth system
    """

    # Camera settings
    camera_resolution_width = models.IntegerField(default=1920)
    camera_resolution_height = models.IntegerField(default=1080)
    camera_fps = models.IntegerField(default=30)

    # Photo settings
    photo_quality = models.IntegerField(default=95, help_text="JPEG quality (1-100)")
    enable_filters = models.BooleanField(default=True)
    countdown_seconds = models.IntegerField(default=3)

    # UI settings
    welcome_message = models.TextField(default="Welcome to our Wedding Photobooth!")
    instructions = models.TextField(
        default="Position yourselves in front of the camera and smile!"
    )
    show_gallery_preview = models.BooleanField(default=True)

    # Technical settings
    max_photos_per_session = models.IntegerField(default=1000)
    auto_cleanup_days = models.IntegerField(
        default=30, help_text="Delete photos older than X days"
    )

    class Meta:
        verbose_name = "Photobooth Settings"
        verbose_name_plural = "Photobooth Settings"

    def __str__(self):
        return "Photobooth Settings"

    @classmethod
    def get_settings(cls):
        """Get or create the settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
