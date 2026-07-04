from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClient

from .models import Problem, ProblemMedia, ProblemStatus
from .serializers import (
    ProblemCreateSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    ProblemUpdateSerializer,
)
from .services import (
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