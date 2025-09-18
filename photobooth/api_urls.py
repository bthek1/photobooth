from django.urls import path

from . import api_views

app_name = "photobooth_api"

urlpatterns = [
    # Authentication
    path(
        "auth/register/", api_views.UserRegistrationAPIView.as_view(), name="register"
    ),
    # Event management
    path("events/", api_views.EventListAPIView.as_view(), name="event-list"),
    path("events/create/", api_views.EventCreateAPIView.as_view(), name="event-create"),
    path(
        "events/<uuid:pk>/", api_views.EventDetailAPIView.as_view(), name="event-detail"
    ),
    path("events/join/", api_views.join_event_api, name="join-event"),
    # Event gallery (public)
    path(
        "events/<uuid:event_id>/gallery/",
        api_views.EventGalleryAPIView.as_view(),
        name="event-gallery",
    ),
    path("events/<uuid:event_id>/info/", api_views.event_info_api, name="event-info"),
    # Photo operations
    path(
        "photos/capture/", api_views.PhotoCaptureAPIView.as_view(), name="photo-capture"
    ),
    path(
        "photos/<uuid:photo_id>/",
        api_views.PhotoDetailAPIView.as_view(),
        name="photo-detail",
    ),
    path(
        "photos/<uuid:photo_id>/download/",
        api_views.photo_download_api,
        name="photo-download",
    ),
    # QR codes
    path("qr/photo/<uuid:photo_id>/", api_views.generate_photo_qr_api, name="photo-qr"),
    path(
        "qr/event/<uuid:event_id>/",
        api_views.generate_event_qr_api,
        name="event-gallery-qr",
    ),
    # Settings
    path("settings/camera/", api_views.camera_settings_api, name="camera-settings"),
]
