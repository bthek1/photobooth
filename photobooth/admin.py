from django.contrib import admin

from .models import Photo, PhotoboothSession, PhotoboothSettings


@admin.register(PhotoboothSession)
class PhotoboothSessionAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "is_active", "photo_count", "created_at"]
    list_filter = ["is_active", "date", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at", "photo_count"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("photos")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "guest_name", "taken_at", "is_processed"]
    list_filter = ["session", "is_processed", "taken_at"]
    search_fields = ["guest_name", "guest_email"]
    readonly_fields = ["id", "taken_at"]
    raw_id_fields = ["session"]


@admin.register(PhotoboothSettings)
class PhotoboothSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not PhotoboothSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
