from django.contrib import admin
from .models import Problem, ProblemMedia


class ProblemMediaInline(admin.TabularInline):
    model = ProblemMedia
    extra = 0

    fields = (
        "media_type",
        "original_filename",
        "file_size",
        "mime_type",
        "storage_provider",
        "public_id",
        "secure_url",
        "uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )

    show_change_link = True


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "short_description",
        "status",
        "source",
        "language",
        "ward",
        "district",
        "submitted_at",
        "created_at",
    )

    list_filter = (
        "status",
        "source",
        "language",
        "state",
        "district",
        "ward",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "client__username",
        "client__email",
        "client__phone_number",
        "pincode",
        "locality",
        "ward",
        "district",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Problem",
            {
                "fields": (
                    "id",
                    "client",
                    "title",
                    "description",
                    "language",
                    "source",
                    "status",
                ),
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "latitude",
                    "longitude",
                    "pincode",
                    "locality",
                    "ward",
                    "district",
                    "state",
                ),
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "submitted_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = (
        ProblemMediaInline,
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    @admin.display(description="Description")
    def short_description(self, obj):
        if len(obj.description) <= 70:
            return obj.description

        return f"{obj.description[:70]}..."


@admin.register(ProblemMedia)
class ProblemMediaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "problem",
        "media_type",
        "original_filename",
        "formatted_file_size",
        "mime_type",
        "storage_provider",
        "uploaded_at",
    )

    list_filter = (
        "media_type",
        "storage_provider",
        "mime_type",
        "uploaded_at",
    )

    search_fields = (
        "public_id",
        "original_filename",
        "mime_type",
    )

    readonly_fields = (
        "id",
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )

    @admin.display(
        description="File size",
        ordering="file_size",
    )
    def formatted_file_size(self, obj):
        size = obj.file_size

        if size < 1024:
            return f"{size} B"

        if size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"

        return f"{size / (1024 * 1024):.2f} MB"