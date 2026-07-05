import uuid

from django.db import models

from problems.models import Problem


class IssueStatus(models.TextChoices):
    IDENTIFIED = "IDENTIFIED", "Identified"
    PRIORITIZED = "PRIORITIZED", "Prioritized"
    PROPOSAL_READY = "PROPOSAL_READY", "Proposal Ready"
    PENDING_MP_REVIEW = "PENDING_MP_REVIEW", "Pending MP Review"
    APPROVED = "APPROVED", "Approved"
    APPROVED_WITH_CHANGES = (
        "APPROVED_WITH_CHANGES",
        "Approved With Changes",
    )


class Issue(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    title = models.CharField(
        max_length=300,
    )

    summary = models.TextField()

    category = models.CharField(
        max_length=100,
        db_index=True,
    )

    subcategory = models.CharField(
        max_length=100,
        blank=True,
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

    priority_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )

    priority_reasoning = models.TextField(
        blank=True,
    )

    estimated_affected_population = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=40,
        choices=IssueStatus.choices,
        default=IssueStatus.IDENTIFIED,
        db_index=True,
    )

    problems = models.ManyToManyField(
        Problem,
        through="IssueProblem",
        related_name="issues",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-priority_score",
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "status",
                    "priority_score",
                ],
            ),
            models.Index(
                fields=[
                    "category",
                    "district",
                    "ward",
                ],
            ),
        ]

    def __str__(self):
        return self.title


class IssueProblem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="problem_links",
    )

    problem = models.ForeignKey(
        Problem,
        on_delete=models.PROTECT,
        related_name="issue_links",
    )

    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )

    ai_reasoning = models.TextField(
        blank=True,
    )

    linked_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "issue",
                    "problem",
                ],
                name="unique_issue_problem",
            ),
        ]

        ordering = [
            "linked_at",
        ]

    def __str__(self):
        return (
            f"{self.problem_id} -> "
            f"{self.issue_id}"
        )

class ProposalStatus(models.TextChoices):
    AI_DRAFT = "AI_DRAFT", "AI Draft"

    PENDING_MP_REVIEW = (
        "PENDING_MP_REVIEW",
        "Pending MP Review",
    )

    APPROVED = "APPROVED", "Approved"

    APPROVED_WITH_CHANGES = (
        "APPROVED_WITH_CHANGES",
        "Approved With Changes",
    )


class DevelopmentProposal(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    issue = models.OneToOneField(
        Issue,
        on_delete=models.CASCADE,
        related_name="proposal",
    )

    proposed_solution = models.TextField()

    proposed_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    budget_reasoning = models.TextField(
        blank=True,
    )

    implementation_plan = models.TextField(
        blank=True,
    )

    expected_impact = models.TextField(
        blank=True,
    )

    estimated_duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    final_solution = models.TextField(
        blank=True,
    )

    final_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    mp_notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=40,
        choices=ProposalStatus.choices,
        default=ProposalStatus.AI_DRAFT,
        db_index=True,
    )

    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_proposals",
    )

    reviewed_at = models.DateTimeField(
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
        ordering = [
            "-issue__priority_score",
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"Proposal for {self.issue.title}"
        )