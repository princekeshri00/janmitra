import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ProblemStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    READY_FOR_AI = "READY_FOR_AI", "Ready for AI"
    AI_PROCESSING = "AI_PROCESSING", "AI Processing"
    ANALYZED = "ANALYZED", "Analyzed"
    GROUPED = "GROUPED", "Grouped"
    CLOSED = "CLOSED", "Closed"
    REJECTED = "REJECTED", "Rejected"


class SubmissionSource(models.TextChoices):
    WEB = "WEB", "Web"
    MOBILE = "MOBILE", "Mobile"
    WHATSAPP = "WHATSAPP", "WhatsApp"
    KIOSK = "KIOSK", "Kiosk"
    API = "API", "External API"


class MediaType(models.TextChoices):
    IMAGE = "IMAGE", "Image"
    VIDEO = "VIDEO", "Video"
    AUDIO = "AUDIO", "Audio"


class Problem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="problems",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField()

    language = models.CharField(
        max_length=10,
        default="en",
    )

    source = models.CharField(
        max_length=20,
        choices=SubmissionSource.choices,
        default=SubmissionSource.WEB,
    )

    status = models.CharField(
        max_length=30,
        choices=ProblemStatus.choices,
        default=ProblemStatus.DRAFT,
        db_index=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    pincode = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
    )

    locality = models.CharField(
        max_length=200,
        blank=True,
    )

    ward = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["status", "created_at"],
            ),
            models.Index(
                fields=["district", "ward"],
            ),
        ]

    def __str__(self):
        return f"{self.id} - {self.status}"


class ProblemMedia(models.Model):
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    MAX_VIDEO_SIZE = 50 * 1024 * 1024
    MAX_AUDIO_SIZE = 20 * 1024 * 1024

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="media",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
    )

    storage_provider = models.CharField(
        max_length=50,
        default="CLOUDINARY",
    )

    public_id = models.CharField(
        max_length=500,
    )

    resource_type = models.CharField(
        max_length=50,
    )

    secure_url = models.URLField(
        max_length=1000,
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
    )

    file_size = models.PositiveBigIntegerField()

    original_filename = models.CharField(
        max_length=255,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["uploaded_at"]

    def clean(self):
        super().clean()

        size_limits = {
            MediaType.IMAGE: self.MAX_IMAGE_SIZE,
            MediaType.VIDEO: self.MAX_VIDEO_SIZE,
            MediaType.AUDIO: self.MAX_AUDIO_SIZE,
        }

        limit = size_limits.get(self.media_type)

        if limit and self.file_size > limit:
            limit_mb = limit // (1024 * 1024)

            raise ValidationError(
                {
                    "file_size": (
                        f"{self.media_type.lower()} files "
                        f"cannot exceed {limit_mb} MB."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.problem_id} - {self.media_type}"