from rest_framework import serializers

from .models import (
    MediaType,
    Problem,
    ProblemMedia,
    ProblemStatus,
)


class ProblemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemMedia

        fields = (
            "id",
            "media_type",
            "secure_url",
            "mime_type",
            "file_size",
            "original_filename",
            "uploaded_at",
        )

        read_only_fields = fields


class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem

        fields = (
            "id",
            "title",
            "description",
            "language",
            "source",
            "latitude",
            "longitude",
            "pincode",
            "locality",
            "ward",
            "district",
            "state",
        )

        read_only_fields = (
            "id",
        )

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Problem description cannot be empty."
            )

        return value

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        if (
            latitude is None
            and longitude is not None
        ):
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "Latitude is required when longitude is provided."
                    )
                }
            )

        if (
            latitude is not None
            and longitude is None
        ):
            raise serializers.ValidationError(
                {
                    "longitude": (
                        "Longitude is required when latitude is provided."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        return Problem.objects.create(
            client=request.user,
            status=ProblemStatus.DRAFT,
            **validated_data,
        )


class ProblemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem

        fields = (
            "title",
            "description",
            "language",
            "latitude",
            "longitude",
            "pincode",
            "locality",
            "ward",
            "district",
            "state",
        )

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Problem description cannot be empty."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        latitude = attrs.get(
            "latitude",
            instance.latitude,
        )

        longitude = attrs.get(
            "longitude",
            instance.longitude,
        )

        if (
            latitude is None
            and longitude is not None
        ):
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "Latitude is required when longitude is provided."
                    )
                }
            )

        if (
            latitude is not None
            and longitude is None
        ):
            raise serializers.ValidationError(
                {
                    "longitude": (
                        "Longitude is required when latitude is provided."
                    )
                }
            )

        return attrs

    def update(self, instance, validated_data):
        if instance.status != ProblemStatus.DRAFT:
            raise serializers.ValidationError(
                "Only draft problems can be edited."
            )

        return super().update(
            instance,
            validated_data,
        )


class ProblemListSerializer(serializers.ModelSerializer):
    media_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Problem

        fields = (
            "id",
            "title",
            "description",
            "status",
            "language",
            "source",
            "locality",
            "ward",
            "district",
            "submitted_at",
            "created_at",
            "updated_at",
            "media_count",
        )

        read_only_fields = fields


class ProblemDetailSerializer(serializers.ModelSerializer):
    media = ProblemMediaSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Problem

        fields = (
            "id",
            "title",
            "description",
            "language",
            "source",
            "status",
            "latitude",
            "longitude",
            "pincode",
            "locality",
            "ward",
            "district",
            "state",
            "submitted_at",
            "created_at",
            "updated_at",
            "media",
        )

        read_only_fields = fields


class MediaAttachSerializer(serializers.Serializer):
    media_type = serializers.ChoiceField(
        choices=MediaType.choices,
    )

    public_id = serializers.CharField(
        max_length=500,
    )

    resource_type = serializers.ChoiceField(
        choices=(
            ("image", "Image"),
            ("video", "Video"),
        ),
    )