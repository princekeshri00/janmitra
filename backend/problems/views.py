from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClient

from .cloudinary_service import (
    generate_upload_signature,
    verify_cloudinary_asset,
)
from .models import Problem, ProblemMedia, ProblemStatus
from .serializers import (
    MediaAttachSerializer,
    ProblemCreateSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    ProblemUpdateSerializer,
)
from .services import (
    attach_media,
    remove_media,
    submit_problem,
)


class ProblemListCreateView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        problems = (
            Problem.objects
            .filter(client=request.user)
            .annotate(media_count=Count("media"))
            .order_by("-created_at")
        )

        serializer = ProblemListSerializer(
            problems,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProblemCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        problem = serializer.save()

        response_serializer = ProblemDetailSerializer(
            problem,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProblemDetailView(APIView):
    permission_classes = [IsClient]

    def get_problem(self, request, problem_id):
        return get_object_or_404(
            Problem,
            id=problem_id,
            client=request.user,
        )

    def get(self, request, problem_id):
        problem = self.get_problem(
            request,
            problem_id,
        )

        serializer = ProblemDetailSerializer(
            problem,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, problem_id):
        problem = self.get_problem(
            request,
            problem_id,
        )

        serializer = ProblemUpdateSerializer(
            problem,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        problem = serializer.save()

        response_serializer = ProblemDetailSerializer(
            problem,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class ProblemSubmitView(APIView):
    permission_classes = [IsClient]

    def post(self, request, problem_id):
        problem = get_object_or_404(
            Problem,
            id=problem_id,
            client=request.user,
        )

        problem = submit_problem(
            problem,
        )

        serializer = ProblemDetailSerializer(
            problem,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProblemMediaDeleteView(APIView):
    permission_classes = [IsClient]

    def delete(
        self,
        request,
        problem_id,
        media_id,
    ):
        problem = get_object_or_404(
            Problem,
            id=problem_id,
            client=request.user,
        )

        media = get_object_or_404(
            ProblemMedia,
            id=media_id,
            problem=problem,
        )

        remove_media(
            problem=problem,
            media=media,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ProblemMediaUploadSignatureView(APIView):
    permission_classes = [IsClient]

    def post(self, request, problem_id):
        problem = get_object_or_404(
            Problem,
            id=problem_id,
            client=request.user,
        )

        if problem.status != ProblemStatus.DRAFT:
            return Response(
                {
                    "detail": (
                        "Media can only be uploaded "
                        "to draft problems."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        media_type = request.data.get(
            "media_type"
        )

        if not media_type:
            return Response(
                {
                    "media_type": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            upload_data = generate_upload_signature(
                problem=problem,
                media_type=media_type,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        return Response(
            upload_data,
            status=status.HTTP_200_OK,
        )

class ProblemMediaAttachView(APIView):
    permission_classes = [IsClient]

    def post(self, request, problem_id):
        problem = get_object_or_404(
            Problem,
            id=problem_id,
            client=request.user,
        )

        serializer = MediaAttachSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        media_type = serializer.validated_data[
            "media_type"
        ]

        public_id = serializer.validated_data[
            "public_id"
        ]

        resource_type = serializer.validated_data[
            "resource_type"
        ]

        try:
            asset = verify_cloudinary_asset(
                problem=problem,
                media_type=media_type,
                public_id=public_id,
                resource_type=resource_type,
            )

            media = attach_media(
                problem=problem,
                media_type=media_type,
                public_id=asset["public_id"],
                resource_type=asset["resource_type"],
                secure_url=asset["secure_url"],
                file_size=asset["file_size"],
                mime_type=asset["mime_type"],
                original_filename=asset[
                    "original_filename"
                ],
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        return Response(
            {
                "id": media.id,
                "media_type": media.media_type,
                "secure_url": media.secure_url,
                "mime_type": media.mime_type,
                "file_size": media.file_size,
                "original_filename": (
                    media.original_filename
                ),
                "uploaded_at": media.uploaded_at,
            },
            status=status.HTTP_201_CREATED,
        )