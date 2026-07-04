from django.urls import path

from .views import (
    ProblemDetailView,
    ProblemListCreateView,
    ProblemMediaDeleteView,
    ProblemSubmitView,
)


urlpatterns = [
    path(
        "",
        ProblemListCreateView.as_view(),
        name="problem-list-create",
    ),
    path(
        "<uuid:problem_id>/",
        ProblemDetailView.as_view(),
        name="problem-detail",
    ),
    path(
        "<uuid:problem_id>/submit/",
        ProblemSubmitView.as_view(),
        name="problem-submit",
    ),
    path(
        "<uuid:problem_id>/media/<uuid:media_id>/",
        ProblemMediaDeleteView.as_view(),
        name="problem-media-delete",
    ),
]