import base64
import json
import uuid
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from .models import Photo, PhotoboothSession, PhotoboothSettings


class PhotoboothView(ListView):
    """Main photobooth interface view"""

    model = PhotoboothSession
    template_name = "photobooth/interface.html"
    context_object_name = "sessions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = PhotoboothSettings.get_settings()
        context["active_session"] = PhotoboothSession.objects.filter(
            is_active=True
        ).first()
        return context


class GalleryView(ListView):
    """Gallery view for displaying photos"""

    model = Photo
    template_name = "photobooth/gallery.html"
    context_object_name = "photos"
    paginate_by = 20

    def get_queryset(self):
        session_id = self.kwargs.get("session_id")
        if session_id:
            return Photo.objects.filter(session_id=session_id, is_processed=True)
        return Photo.objects.filter(is_processed=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.kwargs.get("session_id")
        if session_id:
            context["session"] = get_object_or_404(PhotoboothSession, id=session_id)
        return context


@csrf_exempt
def capture_photo(request):
    """Handle photo capture from webcam"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        image_data = data.get("image")
        session_id = data.get("session_id")
        guest_name = data.get("guest_name", "")
        guest_email = data.get("guest_email", "")

        if not image_data or not session_id:
            return JsonResponse(
                {"error": "Image data and session ID required"}, status=400
            )

        # Get the session
        session = get_object_or_404(PhotoboothSession, id=session_id)

        # Decode base64 image
        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")

        # Create photo record
        photo = Photo.objects.create(
            session=session,
            guest_name=guest_name,
            guest_email=guest_email,
            is_processed=True,
        )

        # Save image
        photo.image.save(f"{photo.id}.{ext}", image_file)

        return JsonResponse(
            {
                "success": True,
                "photo_id": str(photo.id),
                "download_url": photo.download_url,
                "gallery_url": reverse("photobooth:gallery"),
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def photo_download(request, photo_id):
    """Download a photo"""
    photo = get_object_or_404(Photo, id=photo_id)

    if not photo.image:
        raise Http404("Photo not found")

    response = HttpResponse(content_type="image/jpeg")
    response["Content-Disposition"] = (
        f'attachment; filename="photobooth_{photo_id}.jpg"'
    )

    with open(photo.image.path, "rb") as f:
        response.write(f.read())

    return response


def generate_qr_code(request, photo_id):
    """Generate QR code for photo download"""
    photo = get_object_or_404(Photo, id=photo_id)

    # Build full URL for download
    download_url = request.build_absolute_uri(photo.download_url)

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(download_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = f'inline; filename="qr_code_{photo_id}.png"'

    return response


def session_gallery_qr(request, session_id):
    """Generate QR code for session gallery"""
    session = get_object_or_404(PhotoboothSession, id=session_id)

    # Build full URL for gallery
    gallery_url = request.build_absolute_uri(
        reverse("photobooth:session_gallery", kwargs={"session_id": session_id})
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(gallery_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = f'inline; filename="gallery_qr_{session_id}.png"'

    return response


def get_camera_settings(request):
    """Get camera settings for frontend"""
    settings = PhotoboothSettings.get_settings()
    return JsonResponse(
        {
            "resolution": {
                "width": settings.camera_resolution_width,
                "height": settings.camera_resolution_height,
            },
            "fps": settings.camera_fps,
            "countdown": settings.countdown_seconds,
            "quality": settings.photo_quality,
        }
    )


def get_active_session(request):
    """Get active session for frontend"""
    session = PhotoboothSession.objects.filter(is_active=True).first()
    if session:
        return JsonResponse(
            {
                "id": str(session.id),
                "name": session.name,
                "photo_count": session.photo_count,
            }
        )
    return JsonResponse({"error": "No active session"}, status=404)
