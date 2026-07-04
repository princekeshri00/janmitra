from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import MediaType, ProblemMedia, ProblemStatus


MAX_IMAGES_PER_PROBLEM = 5
MAX_VIDEOS_PER_PROBLEM = 2
MAX_AUDIO_PER_PROBLEM = 1

MAX_TOTAL_MEDIA_SIZE = 100 * 1024 * 1024


def validate_problem_is_draft(problem):
    if problem.status != ProblemStatus.DRAFT:
        raise ValidationError(
            "Problem can only be modified while it is in draft state."
        )


def validate_media_count(problem, media_type):
    media_count = problem.media.filter(
        media_type=media_type,
    ).count()

    limits = {
        MediaType.IMAGE: MAX_IMAGES_PER_PROBLEM,
        MediaType.VIDEO: MAX_VIDEOS_PER_PROBLEM,
        MediaType.AUDIO: MAX_AUDIO_PER_PROBLEM,
    }

    limit = limits.get(media_type)

    if limit is None:
        raise ValidationError(
            "Unsupported media type."
        )

    if media_count >= limit:
        raise ValidationError(
            f"Maximum {limit} {media_type.lower()} file(s) allowed."
        )


def validate_total_media_size(problem, new_file_size):
    current_size = (
        problem.media.aggregate(
            total=Sum("file_size")
        )["total"]
        or 0
    )

    new_total_size = current_size + new_file_size

    if new_total_size > MAX_TOTAL_MEDIA_SIZE:
        raise ValidationError(
            "Total media size cannot exceed 100 MB."
        )


@transaction.atomic
def attach_media(
    *,
    problem,
    media_type,
    public_id,
    resource_type,
    secure_url,
    file_size,
    mime_type="",
    original_filename="",
):
    validate_problem_is_draft(problem)

    validate_media_count(
        problem,
        media_type,
    )

    validate_total_media_size(
        problem,
        file_size,
    )

    media = ProblemMedia.objects.create(
        problem=problem,
        media_type=media_type,
        storage_provider="CLOUDINARY",
        public_id=public_id,
        resource_type=resource_type,
        secure_url=secure_url,
        file_size=file_size,
        mime_type=mime_type,
        original_filename=original_filename,
    )

    return media


@transaction.atomic
def remove_media(*, problem, media):
    validate_problem_is_draft(problem)

    if media.problem_id != problem.id:
        raise ValidationError(
            "Media does not belong to this problem."
        )

    media.delete()


@transaction.atomic
def submit_problem(problem):
    validate_problem_is_draft(problem)

    if not problem.description.strip():
        raise ValidationError(
            "Problem description cannot be empty."
        )

    problem.status = ProblemStatus.SUBMITTED
    problem.submitted_at = timezone.now()

    problem.save(
        update_fields=[
            "status",
            "submitted_at",
            "updated_at",
        ]
    )

    return problem


@transaction.atomic
def mark_problem_ready_for_ai(problem):
    if problem.status != ProblemStatus.SUBMITTED:
        raise ValidationError(
            "Only submitted problems can be marked ready for AI."
        )

    problem.status = ProblemStatus.READY_FOR_AI

    problem.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return problem