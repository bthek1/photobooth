from django.contrib import admin

from .models import Event, Photo, PhotoboothSettings


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "date",
        "is_active",
        "created_by",
        "photo_count",
        "created_at",
    ]
    list_filter = ["is_active", "date", "created_at", "created_by"]
    search_fields = ["name", "code", "created_by__username"]
    readonly_fields = ["id", "code", "created_at", "updated_at", "photo_count"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("photos")
            .select_related("created_by")
        )

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "guest_name", "taken_at", "is_processed"]
    list_filter = ["session", "is_processed", "taken_at"]
    search_fields = ["guest_name", "guest_email", "session__name", "session__code"]
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
