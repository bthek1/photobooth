import base64
import json
import uuid
from io import BytesIO

import qrcode
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView

from .forms import CustomUserCreationForm, EventCodeForm, EventForm
from .models import Event, Photo, PhotoboothSettings


# Authentication Views
def signup_view(request):
    """User registration view"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Account created successfully!")
            return redirect("photobooth:event_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "account/signup.html", {"form": form})


# Event Management Views
class EventListView(LoginRequiredMixin, ListView):
    """List user's events"""

    model = Event
    template_name = "photobooth/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)


class EventCreateView(LoginRequiredMixin, CreateView):
    """Create new event"""

    model = Event
    form_class = EventForm
    template_name = "photobooth/event_create.html"
    success_url = reverse_lazy("photobooth:event_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f'Event "{form.instance.name}" created with code: {form.instance.code}',
        )
        return super().form_valid(form)


class EventDetailView(LoginRequiredMixin, DetailView):
    """Event detail view for owners"""

    model = Event
    template_name = "photobooth/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)


def join_event_view(request):
    """Join event with code"""
    if request.method == "POST":
        form = EventCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            event = Event.objects.get(code=code, is_active=True)
            return redirect("photobooth:event_booth", event_id=event.id)
    else:
        form = EventCodeForm()
    return render(request, "photobooth/join_event.html", {"form": form})


# Photobooth Interface Views
def event_booth_view(request, event_id):
    """Main photobooth interface for an event"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    settings = PhotoboothSettings.get_settings()
    return render(
        request, "photobooth/booth.html", {"event": event, "settings": settings}
    )


class EventGalleryView(ListView):
    """Gallery view for an event's photos"""

    model = Photo
    template_name = "photobooth/gallery.html"
    context_object_name = "photos"
    paginate_by = 20

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return Photo.objects.filter(session_id=event_id, is_processed=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get("event_id")
        context["event"] = get_object_or_404(Event, id=event_id)
        return context


# Photo Management Views
@csrf_exempt
def capture_photo(request):
    """Handle photo capture from webcam"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        image_data = data.get("image")
        event_id = data.get("event_id")
        guest_name = data.get("guest_name", "")
        guest_email = data.get("guest_email", "")

        if not image_data or not event_id:
            return JsonResponse(
                {"error": "Image data and event ID required"}, status=400
            )

        # Get the event
        event = get_object_or_404(Event, id=event_id, is_active=True)

        # Decode base64 image
        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")

        # Create photo record
        photo = Photo.objects.create(
            session=event,
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
                "gallery_url": reverse(
                    "photobooth:event_gallery", kwargs={"event_id": event_id}
                ),
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


def event_gallery_qr(request, event_id):
    """Generate QR code for event gallery"""
    event = get_object_or_404(Event, id=event_id)

    # Build full URL for gallery
    gallery_url = request.build_absolute_uri(
        reverse("photobooth:event_gallery", kwargs={"event_id": event_id})
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
    response["Content-Disposition"] = f'inline; filename="gallery_qr_{event_id}.png"'

    return response


# API Views
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


def get_event_info(request, event_id):
    """Get event information for frontend"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return JsonResponse(
        {
            "id": str(event.id),
            "name": event.name,
            "code": event.code,
            "photo_count": event.photo_count,
        }
    )


# Home/Landing Views
def home_view(request):
    """Landing page"""
    return render(request, "photobooth/home.html")
