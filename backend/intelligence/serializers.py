from rest_framework import serializers

from .models import (
    DevelopmentProposal,
    Issue,
    IssueProblem,
)


class IssueProblemSerializer(serializers.ModelSerializer):
    problem_id = serializers.UUIDField(
        source="problem.id",
        read_only=True,
    )

    title = serializers.CharField(
        source="problem.title",
        read_only=True,
    )

    description = serializers.CharField(
        source="problem.description",
        read_only=True,
    )

    language = serializers.CharField(
        source="problem.language",
        read_only=True,
    )

    locality = serializers.CharField(
        source="problem.locality",
        read_only=True,
    )

    ward = serializers.CharField(
        source="problem.ward",
        read_only=True,
    )

    district = serializers.CharField(
        source="problem.district",
        read_only=True,
    )

    submitted_at = serializers.DateTimeField(
        source="problem.submitted_at",
        read_only=True,
    )

    class Meta:
        model = IssueProblem

        fields = (
            "id",
            "problem_id",
            "title",
            "description",
            "language",
            "locality",
            "ward",
            "district",
            "similarity_score",
            "ai_reasoning",
            "submitted_at",
            "linked_at",
        )

        read_only_fields = fields


class IssueListSerializer(serializers.ModelSerializer):
    problem_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Issue

        fields = (
            "id",
            "title",
            "summary",
            "category",
            "subcategory",
            "locality",
            "ward",
            "district",
            "state",
            "priority_score",
            "priority_reasoning",
            "estimated_affected_population",
            "status",
            "problem_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class IssueDetailSerializer(serializers.ModelSerializer):
    problems = IssueProblemSerializer(
        source="problem_links",
        many=True,
        read_only=True,
    )

    problem_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue

        fields = (
            "id",
            "title",
            "summary",
            "category",
            "subcategory",
            "latitude",
            "longitude",
            "locality",
            "ward",
            "district",
            "state",
            "priority_score",
            "priority_reasoning",
            "estimated_affected_population",
            "status",
            "problem_count",
            "problems",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_problem_count(self, obj):
        return obj.problem_links.count()


class ProposalIssueSerializer(serializers.ModelSerializer):
    problems = IssueProblemSerializer(
        source="problem_links",
        many=True,
        read_only=True,
    )

    problem_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue

        fields = (
            "id",
            "title",
            "summary",
            "category",
            "subcategory",
            "latitude",
            "longitude",
            "locality",
            "ward",
            "district",
            "state",
            "priority_score",
            "priority_reasoning",
            "estimated_affected_population",
            "problem_count",
            "problems",
        )

        read_only_fields = fields

    def get_problem_count(self, obj):
        return obj.problem_links.count()


class MPProposalListSerializer(serializers.ModelSerializer):
    issue_id = serializers.UUIDField(
        source="issue.id",
        read_only=True,
    )

    title = serializers.CharField(
        source="issue.title",
        read_only=True,
    )

    summary = serializers.CharField(
        source="issue.summary",
        read_only=True,
    )

    category = serializers.CharField(
        source="issue.category",
        read_only=True,
    )

    locality = serializers.CharField(
        source="issue.locality",
        read_only=True,
    )

    ward = serializers.CharField(
        source="issue.ward",
        read_only=True,
    )

    district = serializers.CharField(
        source="issue.district",
        read_only=True,
    )

    state = serializers.CharField(
        source="issue.state",
        read_only=True,
    )

    priority_score = serializers.DecimalField(
        source="issue.priority_score",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    estimated_affected_population = serializers.IntegerField(
        source="issue.estimated_affected_population",
        read_only=True,
    )

    problem_count = serializers.SerializerMethodField()

    class Meta:
        model = DevelopmentProposal

        fields = (
            "id",
            "issue_id",
            "title",
            "summary",
            "category",
            "locality",
            "ward",
            "district",
            "state",
            "priority_score",
            "estimated_affected_population",
            "problem_count",
            "proposed_budget",
            "final_budget",
            "status",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_problem_count(self, obj):
        return obj.issue.problem_links.count()


class MPProposalDetailSerializer(serializers.ModelSerializer):
    issue = ProposalIssueSerializer(
        read_only=True,
    )

    reviewed_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = DevelopmentProposal

        fields = (
            "id",
            "issue",
            "proposed_solution",
            "proposed_budget",
            "budget_reasoning",
            "implementation_plan",
            "expected_impact",
            "estimated_duration_days",
            "final_solution",
            "final_budget",
            "mp_notes",
            "status",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class ApproveProposalSerializer(serializers.Serializer):
    mp_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class ApproveProposalWithChangesSerializer(
    serializers.Serializer
):
    final_solution = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    final_budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        required=True,
    )

    mp_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class PublicProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        source="issue.title",
        read_only=True,
    )

    summary = serializers.CharField(
        source="issue.summary",
        read_only=True,
    )

    category = serializers.CharField(
        source="issue.category",
        read_only=True,
    )

    locality = serializers.CharField(
        source="issue.locality",
        read_only=True,
    )

    ward = serializers.CharField(
        source="issue.ward",
        read_only=True,
    )

    district = serializers.CharField(
        source="issue.district",
        read_only=True,
    )

    state = serializers.CharField(
        source="issue.state",
        read_only=True,
    )

    priority_score = serializers.DecimalField(
        source="issue.priority_score",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    estimated_affected_population = serializers.IntegerField(
        source="issue.estimated_affected_population",
        read_only=True,
    )

    solution = serializers.CharField(
        source="final_solution",
        read_only=True,
    )

    budget = serializers.DecimalField(
        source="final_budget",
        max_digits=15,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = DevelopmentProposal

        fields = (
            "id",
            "title",
            "summary",
            "category",
            "locality",
            "ward",
            "district",
            "state",
            "priority_score",
            "estimated_affected_population",
            "solution",
            "budget",
            "status",
            "reviewed_at",
        )

        read_only_fields = fields