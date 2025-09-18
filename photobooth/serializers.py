from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Event, Photo

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        # Remove password2 and use password1 as password
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        user = User.objects.create_user(password=password, **validated_data)
        return user


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""

    created_by = serializers.StringRelatedField(read_only=True)
    photo_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "code",
            "date",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "qr_base_url",
            "photo_count",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at", "created_by"]


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""

    class Meta:
        model = Event
        fields = ["name", "qr_base_url"]


class EventJoinSerializer(serializers.Serializer):
    """Serializer for joining events with code"""

    code = serializers.CharField(max_length=8)

    def validate_code(self, value):
        code = value.upper()
        try:
            Event.objects.get(code=code, is_active=True)
            return code
        except Event.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive event code.")


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for Photo model"""

    session = serializers.StringRelatedField(read_only=True)
    download_url = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = [
            "id",
            "session",
            "image",
            "thumbnail",
            "taken_at",
            "guest_name",
            "guest_email",
            "is_processed",
            "download_url",
        ]
        read_only_fields = ["id", "taken_at", "is_processed"]


class PhotoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating photos"""

    image_data = serializers.CharField(
        write_only=True, help_text="Base64 encoded image data"
    )

    class Meta:
        model = Photo
        fields = ["guest_name", "guest_email", "image_data"]

    def validate_image_data(self, value):
        """Validate base64 image data"""
        if not value.startswith("data:image/"):
            raise serializers.ValidationError("Invalid image data format")
        return value


class PhotoMetadataSerializer(serializers.ModelSerializer):
    """Serializer for updating photo metadata only"""

    class Meta:
        model = Photo
        fields = ["guest_name", "guest_email"]
        fields = ["guest_name", "guest_email"]
