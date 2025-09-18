from django.urls import path

from . import views

app_name = "photobooth"

urlpatterns = [
    path("", views.PhotoboothView.as_view(), name="interface"),
    path("gallery/", views.GalleryView.as_view(), name="gallery"),
    path(
        "gallery/<uuid:session_id>/",
        views.GalleryView.as_view(),
        name="session_gallery",
    ),
    # API endpoints
    path("api/capture/", views.capture_photo, name="capture_photo"),
    path("api/camera-settings/", views.get_camera_settings, name="camera_settings"),
    path("api/active-session/", views.get_active_session, name="active_session"),
    # Download and QR codes
    path("download/<uuid:photo_id>/", views.photo_download, name="photo_download"),
    path("qr/<uuid:photo_id>/", views.generate_qr_code, name="photo_qr"),
    path("qr/gallery/<uuid:session_id>/", views.session_gallery_qr, name="gallery_qr"),
]
