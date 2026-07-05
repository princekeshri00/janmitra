from django.contrib import admin

from .models import Issue, IssueProblem


class IssueProblemInline(admin.TabularInline):
    model = IssueProblem
    extra = 0

    fields = (
        "problem",
        "similarity_score",
        "ai_reasoning",
        "linked_at",
    )

    readonly_fields = (
        "linked_at",
    )

    show_change_link = True


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "subcategory",
        "status",
        "priority_score",
        "ward",
        "district",
        "problem_count",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "subcategory",
        "state",
        "district",
        "ward",
        "created_at",
    )

    search_fields = (
        "title",
        "summary",
        "category",
        "subcategory",
        "locality",
        "ward",
        "district",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Issue",
            {
                "fields": (
                    "id",
                    "title",
                    "summary",
                    "category",
                    "subcategory",
                    "status",
                ),
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "latitude",
                    "longitude",
                    "locality",
                    "ward",
                    "district",
                    "state",
                ),
            },
        ),
        (
            "Priority",
            {
                "fields": (
                    "priority_score",
                    "priority_reasoning",
                    "estimated_affected_population",
                ),
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = (
        IssueProblemInline,
    )

    ordering = (
        "-priority_score",
        "-created_at",
    )

    list_per_page = 50

    @admin.display(description="Problems")
    def problem_count(self, obj):
        return obj.problem_links.count()


@admin.register(IssueProblem)
class IssueProblemAdmin(admin.ModelAdmin):
    list_display = (
        "problem",
        "issue",
        "similarity_score",
        "linked_at",
    )

    list_filter = (
        "issue__category",
        "issue__status",
        "linked_at",
    )

    search_fields = (
        "issue__title",
        "problem__title",
        "problem__description",
    )

    readonly_fields = (
        "id",
        "linked_at",
    )

    ordering = (
        "-linked_at",
    )