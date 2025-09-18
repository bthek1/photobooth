from django.urls import path

from . import views

app_name = "photobooth"

urlpatterns = [
    # Home and authentication
    path("", views.home_view, name="home"),
    # Event management (requires login)
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/create/", views.event_create_view, name="event_create"),
    path(
        "events/<uuid:pk>/",
        views.EventDetailView.as_view(),
        name="event_detail",
    ),
    # Public event access
    path("join/", views.join_event_view, name="join_event"),
    path("event/<uuid:event_id>/booth/", views.event_booth_view, name="event_booth"),
    path(
        "event/<uuid:event_id>/gallery/",
        views.EventGalleryView.as_view(),
        name="event_gallery",
    ),
    # Legacy API endpoints (will be deprecated)
    path("api/capture/", views.capture_photo, name="capture_photo"),
    path("api/camera-settings/", views.get_camera_settings, name="camera_settings"),
    path("api/event/<uuid:event_id>/info/", views.get_event_info, name="event_info"),
    # Download and QR codes
    path("download/<uuid:photo_id>/", views.photo_download, name="photo_download"),
    path("qr/photo/<uuid:photo_id>/", views.generate_qr_code, name="photo_qr"),
    path("qr/event/<uuid:event_id>/", views.event_gallery_qr, name="event_gallery_qr"),
]
