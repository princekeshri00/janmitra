import {
    waitForAuth,
    logoutUser,
} from "./firebase.js";

import {
    getCurrentUser,
} from "./api.js";

import {
    API_BASE_URL,
    USER_ROLES,
} from "./config.js";


const proposalList = document.getElementById(
    "proposalList"
);

const pendingCount = document.getElementById(
    "pendingCount"
);

const approvedCount = document.getElementById(
    "approvedCount"
);

const requestCount = document.getElementById(
    "requestCount"
);

const logoutButton = document.getElementById(
    "logoutButton"
);


const proposalModal = document.getElementById(
    "proposalModal"
);

const closeProposalButton = document.getElementById(
    "closeProposalButton"
);

const modalProposalTitle = document.getElementById(
    "modalProposalTitle"
);

const proposalDetail = document.getElementById(
    "proposalDetail"
);

const proposalActions = document.getElementById(
    "proposalActions"
);

const approveButton = document.getElementById(
    "approveButton"
);

const editApproveButton = document.getElementById(
    "editApproveButton"
);


const editModal = document.getElementById(
    "editModal"
);

const closeEditButton = document.getElementById(
    "closeEditButton"
);

const cancelEditButton = document.getElementById(
    "cancelEditButton"
);

const editProposalForm = document.getElementById(
    "editProposalForm"
);

const editSolution = document.getElementById(
    "editSolution"
);

const editBudget = document.getElementById(
    "editBudget"
);


let proposals = [];

let selectedProposalId = null;

let selectedProposal = null;


function escapeHtml(value) {
    const element = document.createElement(
        "div"
    );

    element.textContent = value ?? "";

    return element.innerHTML;
}


function formatCurrency(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "Not available";
    }

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }
    ).format(
        Number(value)
    );
}


function formatStatus(status) {
    return status
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(
            /\b\w/g,
            (character) =>
                character.toUpperCase()
        );
}


function getStatusClass(status) {
    return `status-${status
        .toLowerCase()
        .replaceAll("_", "-")}`;
}


async function apiRequest(
    endpoint,
    options = {}
) {
    const user = await waitForAuth();

    if (!user) {
        throw new Error(
            "Authentication required."
        );
    }

    const token = await user.getIdToken();

    const headers = {
        Authorization: `Bearer ${token}`,
        ...options.headers,
    };

    if (
        options.body &&
        !(options.body instanceof FormData)
    ) {
        headers["Content-Type"] =
            "application/json";
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers,
        }
    );

    let data = null;

    try {
        data = await response.json();

    } catch {
        data = null;
    }

    if (!response.ok) {
        const error = new Error(
            data?.detail ||
            "API request failed."
        );

        error.status = response.status;

        error.data = data;

        throw error;
    }

    return data;
}


async function getMPProposals() {
    return apiRequest(
        "/intelligence/mp/proposals/"
    );
}


async function getMPProposal(
    proposalId
) {
    return apiRequest(
        `/intelligence/mp/proposals/${proposalId}/`
    );
}


async function approveProposalAPI(
    proposalId
) {
    return apiRequest(
        `/intelligence/mp/proposals/${proposalId}/approve/`,
        {
            method: "POST",

            body: JSON.stringify({
                mp_notes: "",
            }),
        }
    );
}


async function approveProposalWithChangesAPI(
    proposalId,
    payload
) {
    return apiRequest(
        `/intelligence/mp/proposals/${proposalId}/approve-with-changes/`,
        {
            method: "POST",

            body: JSON.stringify(
                payload
            ),
        }
    );
}


function updateSummary() {
    const pending = proposals.filter(
        (proposal) =>
            proposal.status ===
            "PENDING_MP_REVIEW"
    ).length;

    const approved = proposals.filter(
        (proposal) =>
            proposal.status ===
            "APPROVED" ||
            proposal.status ===
            "APPROVED_WITH_CHANGES"
    ).length;

    const requests = proposals.reduce(
        (total, proposal) =>
            total +
            Number(
                proposal.problem_count || 0
            ),
        0
    );

    pendingCount.textContent = pending;

    approvedCount.textContent = approved;

    requestCount.textContent = requests;
}


function renderProposals() {
    proposalList.innerHTML = "";

    if (!proposals.length) {
        proposalList.innerHTML = `
            <div class="empty-state">

                <h3>
                    No development proposals
                </h3>

                <p>
                    Prioritized proposals will appear
                    here after the intelligence pipeline
                    runs.
                </p>

            </div>
        `;

        updateSummary();

        return;
    }


    for (const proposal of proposals) {
        const card = document.createElement(
            "article"
        );

        card.className = "proposal-card";

        card.innerHTML = `
            <div class="priority-score">

                <strong>
                    ${escapeHtml(
            proposal.priority_score
        )}
                </strong>

                <span>
                    Priority
                </span>

            </div>


            <div class="proposal-card-content">

                <div class="proposal-topline">

                    <span class="proposal-category">
                        ${escapeHtml(
            proposal.category
        )}
                    </span>

                    <span
                        class="
                            status-badge
                            ${getStatusClass(
            proposal.status
        )}
                        "
                    >
                        ${escapeHtml(
            formatStatus(
                proposal.status
            )
        )}
                    </span>

                </div>


                <h3>
                    ${escapeHtml(
            proposal.title
        )}
                </h3>


                <p class="proposal-summary">
                    ${escapeHtml(
            proposal.summary
        )}
                </p>


                <div class="proposal-meta">

                    <span>
                        ${escapeHtml(
            [
                proposal.locality,
                proposal.ward,
                proposal.district,
                proposal.state,
            ]
                .filter(Boolean)
                .join(", ")
        )}
                    </span>

                    <span>
                        ${proposal.problem_count}
                        citizen request${proposal.problem_count === 1
                ? ""
                : "s"
            }
                    </span>

                    <span>
                        ${formatCurrency(
                proposal.final_budget ||
                proposal.proposed_budget
            )}
                    </span>

                </div>

            </div>


            <div class="proposal-card-action">

                <button
                    class="
                        secondary-button
                        review-button
                    "
                    type="button"
                    data-proposal-id="${proposal.id}"
                >
                    ${proposal.status ===
                "PENDING_MP_REVIEW"
                ? "Review"
                : "View"
            }
                </button>

            </div>
        `;

        proposalList.appendChild(
            card
        );
    }


    const buttons =
        document.querySelectorAll(
            "[data-proposal-id]"
        );

    for (const button of buttons) {
        button.addEventListener(
            "click",
            () => {
                openProposal(
                    button.dataset.proposalId
                );
            }
        );
    }


    updateSummary();
}


function renderProblemEvidence(problems) {
    if (!problems.length) {
        return `
            <p>
                No citizen request evidence available.
            </p>
        `;
    }

    return problems
        .map(
            (problem) => `
                <article class="problem-evidence">

                    <strong>
                        ${escapeHtml(
                problem.title
            )}
                    </strong>

                    <p>
                        ${escapeHtml(
                problem.description
            )}
                    </p>

                </article>
            `
        )
        .join("");
}


async function openProposal(
    proposalId
) {
    try {
        selectedProposalId = proposalId;

        selectedProposal =
            await getMPProposal(
                proposalId
            );

        const proposal = selectedProposal;

        const issue = proposal.issue;

        modalProposalTitle.textContent =
            issue.title;


        proposalDetail.innerHTML = `
            <div class="proposal-detail-grid">

                <div class="proposal-stat">

                    <span>
                        Priority Score
                    </span>

                    <strong>
                        ${escapeHtml(
            issue.priority_score
        )} / 100
                    </strong>

                </div>


                <div class="proposal-stat">

                    <span>
                        Citizen Requests
                    </span>

                    <strong>
                        ${issue.problem_count}
                    </strong>

                </div>


                <div class="proposal-stat">

                    <span>
                        Estimated Impact
                    </span>

                    <strong>
                        ${issue
                .estimated_affected_population
                ?.toLocaleString(
                    "en-IN"
                ) ||
            "Not available"
            }
                    </strong>

                </div>

            </div>


            <section class="proposal-section">

                <h3>
                    Consolidated Development Need
                </h3>

                <p>
                    ${escapeHtml(
                issue.summary
            )}
                </p>

            </section>


            <section class="proposal-section">

                <h3>
                    Priority Intelligence
                </h3>

                <div class="reasoning-box">

                    <p>
                        ${escapeHtml(
                issue.priority_reasoning
            )}
                    </p>

                </div>

            </section>


            <section class="proposal-section">

                <h3>
                    AI Proposed Development Solution
                </h3>

                <p>
                    ${escapeHtml(
                proposal.proposed_solution
            )}
                </p>

            </section>


            <section class="proposal-section">

                <h3>
                    Proposed Budget
                </h3>

                <p>
                    <strong>
                        ${formatCurrency(
                proposal.proposed_budget
            )}
                    </strong>
                </p>

                <p>
                    ${escapeHtml(
                proposal.budget_reasoning
            )}
                </p>

            </section>


            <section class="proposal-section">

                <h3>
                    Implementation Plan
                </h3>

                <p>
                    ${escapeHtml(
                proposal.implementation_plan
            )}
                </p>

            </section>


            <section class="proposal-section">

                <h3>
                    Expected Impact
                </h3>

                <p>
                    ${escapeHtml(
                proposal.expected_impact
            )}
                </p>

            </section>


            <section class="proposal-section">

                <h3>
                    Estimated Duration
                </h3>

                <p>
                    <strong>
                        ${proposal
                .estimated_duration_days
            } days
                    </strong>
                </p>

            </section>


            ${proposal.final_solution
                ? `
                        <section class="proposal-section">

                            <h3>
                                MP Final Decision
                            </h3>

                            <p>
                                ${escapeHtml(
                    proposal.final_solution
                )}
                            </p>

                            <p>
                                <strong>
                                    ${formatCurrency(
                    proposal.final_budget
                )}
                                </strong>
                            </p>

                        </section>
                    `
                : ""
            }


            <section class="proposal-section">

                <h3>
                    Citizen Request Evidence
                </h3>

                <div class="problem-evidence-list">

                    ${renderProblemEvidence(
                issue.problems
            )}

                </div>

            </section>
        `;


        if (
            proposal.status ===
            "PENDING_MP_REVIEW"
        ) {
            proposalActions.classList.remove(
                "hidden"
            );

        } else {
            proposalActions.classList.add(
                "hidden"
            );
        }


        proposalModal.classList.remove(
            "hidden"
        );

    } catch (error) {
        console.error(error);

        alert(
            error.data?.detail ||
            error.message
        );
    }
}


function closeProposalModal() {
    proposalModal.classList.add(
        "hidden"
    );

    selectedProposalId = null;

    selectedProposal = null;
}


function openEditModal() {
    if (!selectedProposal) {
        return;
    }

    editSolution.value =
        selectedProposal.proposed_solution;

    editBudget.value =
        selectedProposal.proposed_budget;

    proposalModal.classList.add(
        "hidden"
    );

    editModal.classList.remove(
        "hidden"
    );
}


function closeEditModal() {
    editModal.classList.add(
        "hidden"
    );

    editProposalForm.reset();
}


async function handleApprove() {
    if (!selectedProposalId) {
        return;
    }

    approveButton.disabled = true;

    approveButton.textContent =
        "Approving...";

    try {
        await approveProposalAPI(
            selectedProposalId
        );

        closeProposalModal();

        await loadProposals();

    } catch (error) {
        console.error(error);

        alert(
            error.data?.detail ||
            error.message
        );

    } finally {
        approveButton.disabled = false;

        approveButton.textContent =
            "Approve Proposal";
    }
}


async function handleEditAndApprove(
    event
) {
    event.preventDefault();

    if (!selectedProposalId) {
        return;
    }

    const finalSolution =
        editSolution.value.trim();

    const finalBudget = Number(
        editBudget.value
    );

    if (
        !finalSolution ||
        !Number.isFinite(finalBudget) ||
        finalBudget < 0
    ) {
        return;
    }


    try {
        await approveProposalWithChangesAPI(
            selectedProposalId,
            {
                final_solution:
                    finalSolution,

                final_budget:
                    finalBudget,

                mp_notes:
                    "Proposal revised by MP.",
            }
        );

        closeEditModal();

        selectedProposalId = null;

        selectedProposal = null;

        await loadProposals();

    } catch (error) {
        console.error(error);

        alert(
            error.data?.detail ||
            error.message
        );
    }
}


async function loadProposals() {
    proposals = await getMPProposals();

    renderProposals();
}


async function initializeMPPage() {
    try {
        const firebaseUser =
            await waitForAuth();

        if (!firebaseUser) {
            window.location.href =
                "../index.html";

            return;
        }


        const user = await getCurrentUser();

        if (
            user.role !== USER_ROLES.MP &&
            user.role !== USER_ROLES.ADMIN
        ) {
            window.location.href =
                "../index.html";

            return;
        }


        await loadProposals();

    } catch (error) {
        console.error(error);

        await logoutUser();

        window.location.href =
            "../index.html";
    }
}


async function handleLogout() {
    await logoutUser();

    window.location.href =
        "../index.html";
}


closeProposalButton.addEventListener(
    "click",
    closeProposalModal
);


approveButton.addEventListener(
    "click",
    handleApprove
);


editApproveButton.addEventListener(
    "click",
    openEditModal
);


closeEditButton.addEventListener(
    "click",
    closeEditModal
);


cancelEditButton.addEventListener(
    "click",
    closeEditModal
);


editProposalForm.addEventListener(
    "submit",
    handleEditAndApprove
);


logoutButton.addEventListener(
    "click",
    handleLogout
);


proposalModal.addEventListener(
    "click",
    (event) => {
        if (
            event.target === proposalModal
        ) {
            closeProposalModal();
        }
    }
);


editModal.addEventListener(
    "click",
    (event) => {
        if (
            event.target === editModal
        ) {
            closeEditModal();
        }
    }
);


document.addEventListener(
    "keydown",
    (event) => {
        if (event.key !== "Escape") {
            return;
        }

        closeProposalModal();

        closeEditModal();
    }
);


initializeMPPage();