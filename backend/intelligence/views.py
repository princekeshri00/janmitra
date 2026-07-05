from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsManagementOrAdmin,
    IsMPOrAdmin,
)

from .models import (
    DevelopmentProposal,
    Issue,
    IssueStatus,
    ProposalStatus,
)
from .serializers import (
    ApproveProposalSerializer,
    ApproveProposalWithChangesSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    MPProposalDetailSerializer,
    MPProposalListSerializer,
    PublicProjectSerializer,
)
from .services import (
    run_full_intelligence_pipeline,
    run_problem_consolidation,
)


class IssueListView(APIView):
    permission_classes = [IsManagementOrAdmin]

    def get(self, request):
        issues = (
            Issue.objects
            .annotate(
                problem_count=Count(
                    "problem_links"
                )
            )
            .order_by(
                "-priority_score",
                "-created_at",
            )
        )

        serializer = IssueListSerializer(
            issues,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class IssueDetailView(APIView):
    permission_classes = [IsManagementOrAdmin]

    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.prefetch_related(
                "problem_links__problem"
            ),
            id=issue_id,
        )

        serializer = IssueDetailSerializer(
            issue,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class RunConsolidationView(APIView):
    permission_classes = [IsManagementOrAdmin]

    def post(self, request):
        try:
            created_issues = (
                run_problem_consolidation()
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        except RuntimeError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        issues = (
            Issue.objects
            .filter(
                id__in=[
                    issue.id
                    for issue in created_issues
                ]
            )
            .annotate(
                problem_count=Count(
                    "problem_links"
                )
            )
            .order_by(
                "-created_at"
            )
        )

        serializer = IssueListSerializer(
            issues,
            many=True,
        )

        return Response(
            {
                "created_issue_count": (
                    len(created_issues)
                ),
                "issues": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class RunFullPipelineView(APIView):
    permission_classes = [IsManagementOrAdmin]

    def post(self, request):
        try:
            result = (
                run_full_intelligence_pipeline()
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        except RuntimeError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        created_issues = result[
            "created_issues"
        ]

        prioritized_issues = result[
            "prioritized_issues"
        ]

        created_proposals = result[
            "created_proposals"
        ]

        proposals = (
            DevelopmentProposal.objects
            .filter(
                id__in=[
                    proposal.id
                    for proposal in created_proposals
                ]
            )
            .select_related(
                "issue"
            )
            .prefetch_related(
                "issue__problem_links__problem"
            )
            .order_by(
                "-issue__priority_score",
                "-created_at",
            )
        )

        serializer = MPProposalListSerializer(
            proposals,
            many=True,
        )

        return Response(
            {
                "created_issue_count": (
                    len(created_issues)
                ),
                "prioritized_issue_count": (
                    len(prioritized_issues)
                ),
                "created_proposal_count": (
                    len(created_proposals)
                ),
                "proposals": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MPProposalListView(APIView):
    permission_classes = [IsMPOrAdmin]

    def get(self, request):
        proposals = (
            DevelopmentProposal.objects
            .select_related(
                "issue"
            )
            .prefetch_related(
                "issue__problem_links"
            )
            .order_by(
                "-issue__priority_score",
                "-created_at",
            )
        )

        serializer = MPProposalListSerializer(
            proposals,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class MPProposalDetailView(APIView):
    permission_classes = [IsMPOrAdmin]

    def get(
        self,
        request,
        proposal_id,
    ):
        proposal = get_object_or_404(
            DevelopmentProposal.objects
            .select_related(
                "issue",
                "reviewed_by",
            )
            .prefetch_related(
                "issue__problem_links__problem"
            ),
            id=proposal_id,
        )

        serializer = MPProposalDetailSerializer(
            proposal,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ApproveProposalView(APIView):
    permission_classes = [IsMPOrAdmin]

    @transaction.atomic
    def post(
        self,
        request,
        proposal_id,
    ):
        proposal = get_object_or_404(
            DevelopmentProposal.objects
            .select_for_update()
            .select_related(
                "issue"
            ),
            id=proposal_id,
        )

        if (
            proposal.status
            != ProposalStatus.PENDING_MP_REVIEW
        ):
            return Response(
                {
                    "detail": (
                        "Only proposals pending MP review "
                        "can be approved."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ApproveProposalSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        proposal.final_solution = (
            proposal.proposed_solution
        )

        proposal.final_budget = (
            proposal.proposed_budget
        )

        proposal.mp_notes = (
            serializer.validated_data[
                "mp_notes"
            ]
        )

        proposal.status = (
            ProposalStatus.APPROVED
        )

        proposal.reviewed_by = request.user

        proposal.reviewed_at = timezone.now()

        proposal.save(
            update_fields=[
                "final_solution",
                "final_budget",
                "mp_notes",
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        proposal.issue.status = (
            IssueStatus.APPROVED
        )

        proposal.issue.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        output_serializer = (
            MPProposalDetailSerializer(
                proposal
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ApproveProposalWithChangesView(
    APIView
):
    permission_classes = [IsMPOrAdmin]

    @transaction.atomic
    def post(
        self,
        request,
        proposal_id,
    ):
        proposal = get_object_or_404(
            DevelopmentProposal.objects
            .select_for_update()
            .select_related(
                "issue"
            ),
            id=proposal_id,
        )

        if (
            proposal.status
            != ProposalStatus.PENDING_MP_REVIEW
        ):
            return Response(
                {
                    "detail": (
                        "Only proposals pending MP review "
                        "can be approved with changes."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = (
            ApproveProposalWithChangesSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        proposal.final_solution = (
            serializer.validated_data[
                "final_solution"
            ]
        )

        proposal.final_budget = (
            serializer.validated_data[
                "final_budget"
            ]
        )

        proposal.mp_notes = (
            serializer.validated_data[
                "mp_notes"
            ]
        )

        proposal.status = (
            ProposalStatus.APPROVED_WITH_CHANGES
        )

        proposal.reviewed_by = request.user

        proposal.reviewed_at = timezone.now()

        proposal.save(
            update_fields=[
                "final_solution",
                "final_budget",
                "mp_notes",
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        proposal.issue.status = (
            IssueStatus.APPROVED_WITH_CHANGES
        )

        proposal.issue.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        output_serializer = (
            MPProposalDetailSerializer(
                proposal
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class PublicProjectListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projects = (
            DevelopmentProposal.objects
            .filter(
                status__in=[
                    ProposalStatus.APPROVED,
                    ProposalStatus.APPROVED_WITH_CHANGES,
                ]
            )
            .select_related(
                "issue"
            )
            .order_by(
                "-issue__priority_score",
                "-reviewed_at",
            )
        )

        serializer = PublicProjectSerializer(
            projects,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PublicProjectDetailView(APIView):
    permission_classes = [AllowAny]

    def get(
        self,
        request,
        proposal_id,
    ):
        project = get_object_or_404(
            DevelopmentProposal.objects
            .filter(
                status__in=[
                    ProposalStatus.APPROVED,
                    ProposalStatus.APPROVED_WITH_CHANGES,
                ]
            )
            .select_related(
                "issue"
            ),
            id=proposal_id,
        )

        serializer = PublicProjectSerializer(
            project,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )