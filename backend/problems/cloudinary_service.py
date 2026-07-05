import time
import cloudinary
import cloudinary.api
import cloudinary.utils
from django.core.exceptions import ValidationError
from .models import MediaType


UPLOAD_SIGNATURE_TTL = 10 * 60


def generate_upload_signature(*, problem, media_type):
    if media_type not in MediaType.values:
        raise ValidationError(
            "Unsupported media type."
        )

    timestamp = int(time.time())

    folder = (
        f"janmitra/problems/{problem.id}"
    )

    resource_type = get_resource_type(
        media_type
    )

    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
    }

    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        cloudinary.config().api_secret,
    )

    return {
        "timestamp": timestamp,
        "signature": signature,
        "api_key": cloudinary.config().api_key,
        "cloud_name": cloudinary.config().cloud_name,
        "folder": folder,
        "resource_type": resource_type,
        "expires_in": UPLOAD_SIGNATURE_TTL,
    }


def verify_cloudinary_asset(
    *,
    problem,
    media_type,
    public_id,
    resource_type,
):
    expected_resource_type = get_resource_type(
        media_type
    )

    if resource_type != expected_resource_type:
        raise ValidationError(
            "Invalid Cloudinary resource type."
        )

    try:
        asset = cloudinary.api.resource(
            public_id,
            resource_type=resource_type,
        )

    except Exception as exc:
        raise ValidationError(
            "Cloudinary asset could not be verified."
        ) from exc

    expected_folder = (
        f"janmitra/problems/{problem.id}/"
    )

    asset_public_id = asset.get(
        "public_id",
        "",
    )

    if not asset_public_id.startswith(
        expected_folder
    ):
        raise ValidationError(
            "Cloudinary asset does not belong to this problem."
        )

    secure_url = asset.get(
        "secure_url"
    )

    file_size = asset.get(
        "bytes"
    )

    asset_resource_type = asset.get(
        "resource_type"
    )

    asset_format = asset.get(
        "format",
        "",
    )

    original_filename = asset.get(
        "original_filename",
        "",
    )

    if not secure_url:
        raise ValidationError(
            "Cloudinary asset URL is missing."
        )

    if not file_size:
        raise ValidationError(
            "Cloudinary asset file size is missing."
        )

    if asset_resource_type != expected_resource_type:
        raise ValidationError(
            "Cloudinary asset resource type mismatch."
        )

    mime_type = build_mime_type(
        media_type=media_type,
        asset_format=asset_format,
    )

    return {
        "public_id": asset_public_id,
        "resource_type": asset_resource_type,
        "secure_url": secure_url,
        "file_size": file_size,
        "mime_type": mime_type,
        "original_filename": original_filename,
    }


def get_resource_type(media_type):
    resource_types = {
        MediaType.IMAGE: "image",
        MediaType.VIDEO: "video",
        MediaType.AUDIO: "video",
    }

    resource_type = resource_types.get(
        media_type
    )

    if resource_type is None:
        raise ValidationError(
            "Unsupported media type."
        )

    return resource_type


def build_mime_type(
    *,
    media_type,
    asset_format,
):
    if not asset_format:
        return ""

    if media_type == MediaType.IMAGE:
        return f"image/{asset_format}"

    if media_type == MediaType.VIDEO:
        return f"video/{asset_format}"

    if media_type == MediaType.AUDIO:
        return f"audio/{asset_format}"

    return ""