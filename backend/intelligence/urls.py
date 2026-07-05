from django.urls import path

from .views import (
    ApproveProposalView,
    ApproveProposalWithChangesView,
    IssueDetailView,
    IssueListView,
    MPProposalDetailView,
    MPProposalListView,
    PublicProjectDetailView,
    PublicProjectListView,
    RunConsolidationView,
    RunFullPipelineView,
)


urlpatterns = [
    path(
        "issues/",
        IssueListView.as_view(),
        name="issue-list",
    ),

    path(
        "issues/<uuid:issue_id>/",
        IssueDetailView.as_view(),
        name="issue-detail",
    ),

    path(
        "pipeline/consolidate/",
        RunConsolidationView.as_view(),
        name="run-consolidation",
    ),

    path(
        "pipeline/run/",
        RunFullPipelineView.as_view(),
        name="run-full-pipeline",
    ),

    path(
        "mp/proposals/",
        MPProposalListView.as_view(),
        name="mp-proposal-list",
    ),

    path(
        "mp/proposals/<uuid:proposal_id>/",
        MPProposalDetailView.as_view(),
        name="mp-proposal-detail",
    ),

    path(
        "mp/proposals/<uuid:proposal_id>/approve/",
        ApproveProposalView.as_view(),
        name="approve-proposal",
    ),

    path(
        "mp/proposals/<uuid:proposal_id>/approve-with-changes/",
        ApproveProposalWithChangesView.as_view(),
        name="approve-proposal-with-changes",
    ),

    path(
        "public/projects/",
        PublicProjectListView.as_view(),
        name="public-project-list",
    ),

    path(
        "public/projects/<uuid:proposal_id>/",
        PublicProjectDetailView.as_view(),
        name="public-project-detail",
    ),
]