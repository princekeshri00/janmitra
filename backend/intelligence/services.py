from django.core.exceptions import ValidationError
from django.db import transaction

from problems.models import Problem, ProblemStatus

from .gemini_service import (
    consolidate_problems,
    generate_proposals,
    prioritize_issues,
)
from .models import (
    DevelopmentProposal,
    Issue,
    IssueProblem,
    IssueStatus,
    ProposalStatus,
)


def validate_consolidation_result(
    *,
    problems,
    result,
):
    problem_map = {
        str(problem.id): problem
        for problem in problems
    }

    expected_problem_ids = set(
        problem_map.keys()
    )

    returned_problem_ids = []

    for issue in result.issues:
        for grouped_problem in issue.problems:
            returned_problem_ids.append(
                grouped_problem.problem_id
            )

    returned_problem_id_set = set(
        returned_problem_ids
    )

    unknown_problem_ids = (
        returned_problem_id_set
        - expected_problem_ids
    )

    if unknown_problem_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini returned unknown problem IDs: "
                    f"{sorted(unknown_problem_ids)}"
                )
            }
        )

    missing_problem_ids = (
        expected_problem_ids
        - returned_problem_id_set
    )

    if missing_problem_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini did not return problem IDs: "
                    f"{sorted(missing_problem_ids)}"
                )
            }
        )

    duplicate_problem_ids = {
        problem_id
        for problem_id in returned_problem_ids
        if returned_problem_ids.count(
            problem_id
        ) > 1
    }

    if duplicate_problem_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini assigned problems to multiple "
                    "issues: "
                    f"{sorted(duplicate_problem_ids)}"
                )
            }
        )

    if not result.issues:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini returned no consolidated issues."
                )
            }
        )

    for issue in result.issues:
        if not issue.problems:
            raise ValidationError(
                {
                    "gemini_result": (
                        f"Issue '{issue.title}' "
                        "contains no problems."
                    )
                }
            )

    return problem_map


@transaction.atomic
def save_consolidation_result(
    *,
    problems,
    result,
):
    problems = list(problems)

    problem_map = validate_consolidation_result(
        problems=problems,
        result=result,
    )

    created_issues = []

    for consolidated_issue in result.issues:
        issue = Issue.objects.create(
            title=consolidated_issue.title,
            summary=consolidated_issue.summary,
            category=consolidated_issue.category,
            subcategory=(
                consolidated_issue.subcategory
            ),
            locality=consolidated_issue.locality,
            ward=consolidated_issue.ward,
            district=consolidated_issue.district,
            state=consolidated_issue.state,
        )

        issue_problem_links = []

        for grouped_problem in (
            consolidated_issue.problems
        ):
            problem = problem_map[
                grouped_problem.problem_id
            ]

            issue_problem_links.append(
                IssueProblem(
                    issue=issue,
                    problem=problem,
                    similarity_score=(
                        grouped_problem.similarity_score
                    ),
                    ai_reasoning=(
                        grouped_problem.reasoning
                    ),
                )
            )

        IssueProblem.objects.bulk_create(
            issue_problem_links
        )

        created_issues.append(
            issue
        )

    problem_ids = [
        problem.id
        for problem in problems
    ]

    Problem.objects.filter(
        id__in=problem_ids,
    ).update(
        status=ProblemStatus.GROUPED,
    )

    return created_issues


def run_problem_consolidation():
    problems = list(
        Problem.objects.filter(
            status=ProblemStatus.READY_FOR_AI,
        ).order_by(
            "created_at"
        )
    )

    if not problems:
        return []

    result = consolidate_problems(
        problems
    )

    return save_consolidation_result(
        problems=problems,
        result=result,
    )


def validate_prioritization_result(
    *,
    issues,
    result,
):
    issue_map = {
        str(issue.id): issue
        for issue in issues
    }

    expected_issue_ids = set(
        issue_map.keys()
    )

    returned_issue_ids = [
        prioritized_issue.issue_id
        for prioritized_issue in result.issues
    ]

    returned_issue_id_set = set(
        returned_issue_ids
    )

    unknown_issue_ids = (
        returned_issue_id_set
        - expected_issue_ids
    )

    if unknown_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini returned unknown issue IDs: "
                    f"{sorted(unknown_issue_ids)}"
                )
            }
        )

    missing_issue_ids = (
        expected_issue_ids
        - returned_issue_id_set
    )

    if missing_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini did not prioritize issue IDs: "
                    f"{sorted(missing_issue_ids)}"
                )
            }
        )

    duplicate_issue_ids = {
        issue_id
        for issue_id in returned_issue_ids
        if returned_issue_ids.count(
            issue_id
        ) > 1
    }

    if duplicate_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini prioritized issue IDs more "
                    "than once: "
                    f"{sorted(duplicate_issue_ids)}"
                )
            }
        )

    return issue_map


@transaction.atomic
def save_prioritization_result(
    *,
    issues,
    result,
):
    issues = list(issues)

    issue_map = validate_prioritization_result(
        issues=issues,
        result=result,
    )

    prioritized_issues = []

    for prioritized_issue in result.issues:
        issue = issue_map[
            prioritized_issue.issue_id
        ]

        issue.priority_score = (
            prioritized_issue.priority_score
        )

        issue.priority_reasoning = (
            prioritized_issue.priority_reasoning
        )

        issue.estimated_affected_population = (
            prioritized_issue
            .estimated_affected_population
        )

        issue.status = IssueStatus.PRIORITIZED

        issue.save(
            update_fields=[
                "priority_score",
                "priority_reasoning",
                "estimated_affected_population",
                "status",
                "updated_at",
            ]
        )

        prioritized_issues.append(
            issue
        )

    return prioritized_issues


def run_issue_prioritization():
    issues = list(
        Issue.objects.filter(
            status=IssueStatus.IDENTIFIED,
        ).prefetch_related(
            "problem_links__problem"
        )
    )

    if not issues:
        return []

    result = prioritize_issues(
        issues
    )

    return save_prioritization_result(
        issues=issues,
        result=result,
    )


def validate_proposal_result(
    *,
    issues,
    result,
):
    issue_map = {
        str(issue.id): issue
        for issue in issues
    }

    expected_issue_ids = set(
        issue_map.keys()
    )

    returned_issue_ids = [
        proposal.issue_id
        for proposal in result.proposals
    ]

    returned_issue_id_set = set(
        returned_issue_ids
    )

    unknown_issue_ids = (
        returned_issue_id_set
        - expected_issue_ids
    )

    if unknown_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini returned proposals for unknown "
                    "issue IDs: "
                    f"{sorted(unknown_issue_ids)}"
                )
            }
        )

    missing_issue_ids = (
        expected_issue_ids
        - returned_issue_id_set
    )

    if missing_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini did not generate proposals for "
                    "issue IDs: "
                    f"{sorted(missing_issue_ids)}"
                )
            }
        )

    duplicate_issue_ids = {
        issue_id
        for issue_id in returned_issue_ids
        if returned_issue_ids.count(
            issue_id
        ) > 1
    }

    if duplicate_issue_ids:
        raise ValidationError(
            {
                "gemini_result": (
                    "Gemini generated multiple proposals "
                    "for issue IDs: "
                    f"{sorted(duplicate_issue_ids)}"
                )
            }
        )

    return issue_map


@transaction.atomic
def save_proposal_result(
    *,
    issues,
    result,
):
    issues = list(issues)

    issue_map = validate_proposal_result(
        issues=issues,
        result=result,
    )

    created_proposals = []

    for generated_proposal in result.proposals:
        issue = issue_map[
            generated_proposal.issue_id
        ]

        proposal = DevelopmentProposal.objects.create(
            issue=issue,
            proposed_solution=(
                generated_proposal.proposed_solution
            ),
            proposed_budget=(
                generated_proposal.proposed_budget
            ),
            budget_reasoning=(
                generated_proposal.budget_reasoning
            ),
            implementation_plan=(
                generated_proposal.implementation_plan
            ),
            expected_impact=(
                generated_proposal.expected_impact
            ),
            estimated_duration_days=(
                generated_proposal
                .estimated_duration_days
            ),
            status=(
                ProposalStatus.PENDING_MP_REVIEW
            ),
        )

        issue.status = (
            IssueStatus.PENDING_MP_REVIEW
        )

        issue.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        created_proposals.append(
            proposal
        )

    return created_proposals


def run_proposal_generation():
    issues = list(
        Issue.objects.filter(
            status=IssueStatus.PRIORITIZED,
            proposal__isnull=True,
        ).prefetch_related(
            "problem_links__problem"
        )
    )

    if not issues:
        return []

    result = generate_proposals(
        issues
    )

    return save_proposal_result(
        issues=issues,
        result=result,
    )


def run_full_intelligence_pipeline():
    created_issues = (
        run_problem_consolidation()
    )

    prioritized_issues = (
        run_issue_prioritization()
    )

    created_proposals = (
        run_proposal_generation()
    )

    return {
        "created_issues": created_issues,
        "prioritized_issues": prioritized_issues,
        "created_proposals": created_proposals,
    }