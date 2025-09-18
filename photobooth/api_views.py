import base64
import json
import uuid
from io import BytesIO

import qrcode
from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Photo, PhotoboothSettings
from .serializers import (
    EventCreateSerializer,
    EventJoinSerializer,
    EventSerializer,
    PhotoMetadataSerializer,
    PhotoSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationAPIView(generics.CreateAPIView):
    """API view for user registration"""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response(
                {
                    "message": "Account created successfully!",
                    "user_id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventListAPIView(generics.ListAPIView):
    """API view to list user's events"""

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)


class EventCreateAPIView(generics.CreateAPIView):
    """API view to create new event"""

    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user)
        return event

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = self.perform_create(serializer)
            response_serializer = EventSerializer(event)
            return Response(
                {
                    "message": f'Event "{event.name}" created with code: {event.code}',
                    "event": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for event detail (owner only)"""

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)


@api_view(["POST"])
@permission_classes([AllowAny])
def join_event_api(request):
    """API endpoint to join event with code"""
    serializer = EventJoinSerializer(data=request.data)
    if serializer.is_valid():
        code = serializer.validated_data["code"]
        event = Event.objects.get(code=code, is_active=True)
        return Response(
            {
                "message": f"Successfully joined event: {event.name}",
                "event_id": event.id,
                "redirect_url": f"/photobooth/event/{event.id}/booth/",
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventGalleryAPIView(generics.RetrieveAPIView):
    """API view for event gallery (public access)"""

    queryset = Event.objects.filter(is_active=True)
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"
    lookup_url_kwarg = "event_id"

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        photos = Photo.objects.filter(session=event).order_by("-taken_at")

        # Paginate photos
        page_size = 12
        page = int(request.GET.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size

        photo_serializer = PhotoSerializer(photos[start:end], many=True)

        return Response(
            {
                "event": EventSerializer(event).data,
                "photos": photo_serializer.data,
                "has_next": end < photos.count(),
                "has_previous": page > 1,
                "current_page": page,
                "total_photos": photos.count(),
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class PhotoCaptureAPIView(APIView):
    """API view for capturing photos"""

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
            event_id = data.get("event_id")
            image_data = data.get("image")
            guest_name = data.get("guest_name", "")
            guest_email = data.get("guest_email", "")

            if not event_id or not image_data:
                return JsonResponse(
                    {"error": "Event ID and image data required"}, status=400
                )

            # Get event
            try:
                event = Event.objects.get(id=event_id, is_active=True)
            except Event.DoesNotExist:
                return JsonResponse({"error": "Event not found"}, status=404)

            # Process base64 image
            if image_data.startswith("data:image/"):
                format_data, imgstr = image_data.split(";base64,")
                ext = format_data.split("/")[-1]
                if ext == "jpeg":
                    ext = "jpg"
            else:
                return JsonResponse({"error": "Invalid image format"}, status=400)

            img_data = base64.b64decode(imgstr)

            # Create photo
            photo = Photo.objects.create(
                session=event, guest_name=guest_name, guest_email=guest_email
            )

            # Save image
            photo.image.save(f"{uuid.uuid4()}.{ext}", ContentFile(img_data), save=True)

            return JsonResponse(
                {
                    "success": True,
                    "photo_id": str(photo.id),
                    "download_url": photo.download_url,
                    "message": "Photo captured successfully!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def camera_settings_api(request):
    """API endpoint to get camera settings"""
    settings = PhotoboothSettings.get_settings()
    return Response(
        {
            "resolution": {
                "width": settings.camera_resolution_width,
                "height": settings.camera_resolution_height,
            },
            "fps": settings.camera_fps,
            "countdown": settings.countdown_seconds,
            "quality": settings.photo_quality,
            "welcome_message": settings.welcome_message,
            "instructions": settings.instructions,
            "show_gallery_preview": settings.show_gallery_preview,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def event_info_api(request, event_id):
    """API endpoint to get event information"""
    try:
        event = Event.objects.get(id=event_id, is_active=True)
        return Response(EventSerializer(event).data)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)


class PhotoDetailAPIView(generics.RetrieveUpdateAPIView):
    """API view for photo details and metadata updates"""

    queryset = Photo.objects.all()
    permission_classes = [AllowAny]
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return PhotoMetadataSerializer
        return PhotoSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def photo_download_api(request, photo_id):
    """API endpoint for photo download"""
    photo = get_object_or_404(Photo, id=photo_id)

    try:
        response = HttpResponse(photo.image.read(), content_type="image/jpeg")
        response["Content-Disposition"] = (
            f'attachment; filename="{photo.session.name}_{photo.id}.jpg"'
        )
        return response
    except Exception:
        return JsonResponse({"error": "Photo not found"}, status=404)


@api_view(["GET"])
@permission_classes([AllowAny])
def generate_photo_qr_api(request, photo_id):
    """API endpoint to generate QR code for photo download"""
    photo = get_object_or_404(Photo, id=photo_id)

    # Generate QR code
    download_url = request.build_absolute_uri(photo.download_url)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(download_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@api_view(["GET"])
@permission_classes([AllowAny])
def generate_event_qr_api(request, event_id):
    """API endpoint to generate QR code for event gallery"""
    event = get_object_or_404(Event, id=event_id)

    # Generate QR code for gallery
    gallery_url = request.build_absolute_uri(f"/photobooth/event/{event.id}/gallery/")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(gallery_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")
