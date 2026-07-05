import os

from google import genai
from pydantic import BaseModel, Field


GEMINI_MODEL = "gemini-2.5-flash"


class GroupedProblem(BaseModel):
    problem_id: str = Field(
        description="Exact UUID of the citizen problem."
    )

    similarity_score: float = Field(
        ge=0,
        le=1,
        description=(
            "Semantic similarity of this complaint "
            "to the consolidated issue."
        ),
    )

    reasoning: str = Field(
        description=(
            "Short explanation of why this complaint "
            "belongs to the issue."
        ),
    )


class ConsolidatedIssue(BaseModel):
    title: str = Field(
        description=(
            "Clear development issue title in English."
        )
    )

    summary: str = Field(
        description=(
            "Concise summary of the consolidated "
            "citizen development need."
        )
    )

    category: str = Field(
        description=(
            "Broad development category such as WATER, "
            "ROADS, EDUCATION, HEALTH, SANITATION, "
            "TRANSPORT, ELECTRICITY, or OTHER."
        )
    )

    subcategory: str = Field(
        description=(
            "More specific issue classification."
        )
    )

    locality: str = Field(
        description=(
            "Primary locality derived from complaints. "
            "Use empty string if unknown."
        )
    )

    ward: str = Field(
        description=(
            "Primary ward derived from complaints. "
            "Use empty string if unknown."
        )
    )

    district: str = Field(
        description=(
            "Primary district derived from complaints. "
            "Use empty string if unknown."
        )
    )

    state: str = Field(
        description=(
            "Primary state derived from complaints. "
            "Use empty string if unknown."
        )
    )

    problems: list[GroupedProblem]


class ConsolidationResult(BaseModel):
    issues: list[ConsolidatedIssue]


class PrioritizedIssue(BaseModel):
    issue_id: str = Field(
        description="Exact UUID of the supplied issue."
    )

    priority_score: float = Field(
        ge=0,
        le=100,
        description=(
            "Development priority score from 0 to 100."
        ),
    )

    priority_reasoning: str = Field(
        description=(
            "Clear explanation of why this issue received "
            "the assigned priority score."
        )
    )

    estimated_affected_population: int = Field(
        ge=0,
        description=(
            "Conservative estimate of the population "
            "affected by the development issue."
        ),
    )


class PrioritizationResult(BaseModel):
    issues: list[PrioritizedIssue]


class GeneratedProposal(BaseModel):
    issue_id: str = Field(
        description="Exact UUID of the supplied issue."
    )

    proposed_solution: str = Field(
        description=(
            "Specific and actionable public development "
            "solution for the issue."
        )
    )

    proposed_budget: float = Field(
        ge=0,
        description=(
            "Estimated implementation budget in Indian "
            "rupees."
        ),
    )

    budget_reasoning: str = Field(
        description=(
            "Short explanation of the estimated budget."
        )
    )

    implementation_plan: str = Field(
        description=(
            "Practical phased implementation plan."
        )
    )

    expected_impact: str = Field(
        description=(
            "Expected public development impact."
        )
    )

    estimated_duration_days: int = Field(
        ge=1,
        description=(
            "Estimated implementation duration in days."
        ),
    )


class ProposalGenerationResult(BaseModel):
    proposals: list[GeneratedProposal]


def get_gemini_client():
    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=api_key
    )


def build_problem_payload(problems):
    payload = []

    for problem in problems:
        payload.append(
            {
                "problem_id": str(problem.id),
                "title": problem.title,
                "description": problem.description,
                "language": problem.language,
                "locality": problem.locality,
                "ward": problem.ward,
                "district": problem.district,
                "state": problem.state,
                "latitude": (
                    str(problem.latitude)
                    if problem.latitude is not None
                    else None
                ),
                "longitude": (
                    str(problem.longitude)
                    if problem.longitude is not None
                    else None
                ),
            }
        )

    return payload


def build_issue_payload(issues):
    payload = []

    for issue in issues:
        problem_links = (
            issue.problem_links
            .select_related("problem")
            .all()
        )

        complaints = []

        for link in problem_links:
            complaints.append(
                {
                    "title": link.problem.title,
                    "description": (
                        link.problem.description
                    ),
                    "language": link.problem.language,
                }
            )

        payload.append(
            {
                "issue_id": str(issue.id),
                "title": issue.title,
                "summary": issue.summary,
                "category": issue.category,
                "subcategory": issue.subcategory,
                "locality": issue.locality,
                "ward": issue.ward,
                "district": issue.district,
                "state": issue.state,
                "citizen_request_count": len(
                    complaints
                ),
                "complaints": complaints,
            }
        )

    return payload


def consolidate_problems(problems):
    problems = list(problems)

    if not problems:
        return ConsolidationResult(
            issues=[]
        )

    problem_payload = build_problem_payload(
        problems
    )

    prompt = f"""
You are the complaint consolidation engine for JanMitra,
a public development planning platform for Indian MPs.

You are given citizen development complaints.

Your task is ONLY to consolidate semantically similar
complaints into real-world development issues.

IMPORTANT RULES:

1. Every supplied problem_id must appear in the output.
2. Copy every problem_id exactly. Never modify a UUID.
3. A complaint should normally belong to one issue.
4. Group complaints only when they describe substantially
   the same development need.
5. Location matters. Similar complaints from clearly
   different locations should normally be separate issues.
6. Complaints may be written in different languages.
   Understand their meaning and normalize the issue title
   and summary into English.
7. Do not prioritize issues.
8. Do not propose solutions.
9. Do not estimate budgets.
10. Do not invent locations that are not supported by
    the complaint data.
11. Do not merge broad categories merely because they are
    related.
12. If only one complaint describes a unique issue, create
    a single-complaint issue for it.
13. similarity_score must be between 0 and 1.
14. reasoning must briefly explain why the complaint belongs
    to that consolidated issue.

Citizen complaints:

{problem_payload}
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": (
                ConsolidationResult.model_json_schema()
            ),
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty consolidation response."
        )

    return ConsolidationResult.model_validate_json(
        response.text
    )


def prioritize_issues(issues):
    issues = list(issues)

    if not issues:
        return PrioritizationResult(
            issues=[]
        )

    issue_payload = build_issue_payload(
        issues
    )

    prompt = f"""
You are the development prioritization engine for JanMitra,
a public development planning platform for Indian MPs.

You are given consolidated citizen development issues.

Rank each issue based on public development urgency and
impact.

Evaluate:

- essential service impact
- severity of the development gap
- number of citizen requests
- estimated affected population
- public safety risk
- duration and persistence of the issue
- impact on vulnerable populations
- education or healthcare impact
- geographic concentration of demand
- urgency of government intervention

IMPORTANT RULES:

1. Every supplied issue_id must appear exactly once.
2. Copy issue_id exactly.
3. priority_score must be between 0 and 100.
4. Higher scores mean higher development priority.
5. Do not prioritize based only on complaint count.
6. Essential services and public safety may outweigh raw
   complaint volume.
7. Use a conservative affected population estimate.
8. Do not propose solutions.
9. Do not estimate budgets.
10. Explain the priority score clearly.
11. Compare issues against each other before assigning
    scores.
12. Avoid giving every issue a similarly high score.

Consolidated issues:

{issue_payload}
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": (
                PrioritizationResult.model_json_schema()
            ),
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty prioritization response."
        )

    return PrioritizationResult.model_validate_json(
        response.text
    )


def generate_proposals(issues):
    issues = list(issues)

    if not issues:
        return ProposalGenerationResult(
            proposals=[]
        )

    issue_payload = build_issue_payload(
        issues
    )

    prompt = f"""
You are the public development proposal engine for JanMitra,
a decision-support platform for Indian MPs.

You are given prioritized consolidated development issues.

For every issue, generate one practical development
proposal.

The proposal should be suitable for review by an elected
representative and local development administration.

IMPORTANT RULES:

1. Every supplied issue_id must appear exactly once.
2. Copy issue_id exactly.
3. Generate one proposal for each issue.
4. The solution must directly address the development need.
5. Be specific and operational.
6. Avoid vague solutions such as "authorities should act".
7. proposed_budget must be in Indian rupees.
8. Use a realistic but approximate budget.
9. Clearly explain the main cost assumptions.
10. Do not claim the budget is an official government
    estimate.
11. Give a practical implementation plan.
12. Estimate a realistic duration in days.
13. Explain the expected public impact.
14. Do not change the priority score.
15. Do not merge different issues.

Prioritized development issues:

{issue_payload}
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": (
                ProposalGenerationResult.model_json_schema()
            ),
        },
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty proposal response."
        )

    return ProposalGenerationResult.model_validate_json(
        response.text
    )