import {
    getCurrentUser,
    getMyProblems,
    getProblem,
    createProblem,
    submitProblem,
} from "./api.js";

import {
    logoutUser,
    waitForAuth,
} from "./firebase.js";

import {
    USER_ROLES,
} from "./config.js";


const pageLoader = document.getElementById(
    "pageLoader"
);

const clientApp = document.getElementById(
    "clientApp"
);

const userEmail = document.getElementById(
    "userEmail"
);

const logoutButton = document.getElementById(
    "logoutButton"
);

const problemList = document.getElementById(
    "problemList"
);

const problemCount = document.getElementById(
    "problemCount"
);

const problemEmptyState = document.getElementById(
    "problemEmptyState"
);


const complaintModal = document.getElementById(
    "complaintModal"
);

const openComplaintButton = document.getElementById(
    "openComplaintButton"
);

const closeComplaintButton = document.getElementById(
    "closeComplaintButton"
);

const cancelComplaintButton = document.getElementById(
    "cancelComplaintButton"
);

const complaintForm = document.getElementById(
    "complaintForm"
);

const complaintError = document.getElementById(
    "complaintError"
);

const saveDraftButton = document.getElementById(
    "saveDraftButton"
);

const submitComplaintButton = document.getElementById(
    "submitComplaintButton"
);


const problemTitle = document.getElementById(
    "problemTitle"
);

const problemDescription = document.getElementById(
    "problemDescription"
);

const problemLanguage = document.getElementById(
    "problemLanguage"
);

const problemLocality = document.getElementById(
    "problemLocality"
);

const problemWard = document.getElementById(
    "problemWard"
);

const problemDistrict = document.getElementById(
    "problemDistrict"
);

const problemState = document.getElementById(
    "problemState"
);


const problemModal = document.getElementById(
    "problemModal"
);

const closeProblemButton = document.getElementById(
    "closeProblemButton"
);

const detailTitle = document.getElementById(
    "detailTitle"
);

const problemDetailContent = document.getElementById(
    "problemDetailContent"
);


let currentUser = null;
let problems = [];


function escapeHtml(value) {
    const element = document.createElement(
        "div"
    );

    element.textContent = value ?? "";

    return element.innerHTML;
}


function formatDate(value) {
    if (!value) {
        return "Not available";
    }

    return new Intl.DateTimeFormat(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short",
        }
    ).format(
        new Date(value)
    );
}


function formatStatus(status) {
    return status
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(
            /\b\w/g,
            (character) => character.toUpperCase()
        );
}


function getStatusClass(status) {
    return `status-${status
        .toLowerCase()
        .replaceAll("_", "-")}`;
}


function getLocation(problem) {
    const location = [
        problem.locality,
        problem.ward,
        problem.district,
        problem.state,
    ].filter(Boolean);

    if (!location.length) {
        return "Location not specified";
    }

    return location.join(", ");
}


function setPageReady() {
    pageLoader.classList.add(
        "hidden"
    );

    clientApp.classList.remove(
        "hidden"
    );
}


function openComplaintModal() {
    complaintError.textContent = "";

    complaintModal.classList.remove(
        "hidden"
    );
}


function closeComplaintModal() {
    complaintModal.classList.add(
        "hidden"
    );

    complaintForm.reset();

    problemLanguage.value = "en";

    complaintError.textContent = "";
}


function closeProblemModal() {
    problemModal.classList.add(
        "hidden"
    );

    problemDetailContent.innerHTML = "";
}


function setComplaintLoading(isLoading) {
    saveDraftButton.disabled = isLoading;

    submitComplaintButton.disabled = isLoading;

    saveDraftButton.textContent = isLoading
        ? "Saving..."
        : "Save Draft";

    submitComplaintButton.textContent = isLoading
        ? "Submitting..."
        : "Submit Request";
}


function getComplaintPayload() {
    return {
        title: problemTitle.value.trim(),

        description:
            problemDescription.value.trim(),

        language:
            problemLanguage.value,

        locality:
            problemLocality.value.trim(),

        ward:
            problemWard.value.trim(),

        district:
            problemDistrict.value.trim(),

        state:
            problemState.value.trim(),
    };
}


function validateComplaintPayload(payload) {
    if (!payload.title) {
        throw new Error(
            "Issue title is required."
        );
    }

    if (!payload.description) {
        throw new Error(
            "Issue description is required."
        );
    }
}


function renderProblems() {
    problemList.innerHTML = "";

    problemCount.textContent =
        `${problems.length} ${problems.length === 1
            ? "request"
            : "requests"
        }`;

    if (!problems.length) {
        problemEmptyState.classList.remove(
            "hidden"
        );

        return;
    }

    problemEmptyState.classList.add(
        "hidden"
    );

    for (const problem of problems) {
        const card = document.createElement(
            "article"
        );

        card.className = "problem-card";

        card.innerHTML = `
            <div class="problem-main">

                <div class="problem-topline">

                    <span
                        class="
                            status-badge
                            ${getStatusClass(problem.status)}
                        "
                    >
                        ${escapeHtml(
            formatStatus(problem.status)
        )}
                    </span>

                </div>

                <h3>
                    ${escapeHtml(problem.title)}
                </h3>

                <p class="problem-description">
                    ${escapeHtml(problem.description)}
                </p>

                <div class="problem-meta">

                    <span>
                        ${escapeHtml(
            getLocation(problem)
        )}
                    </span>

                    <span>
                        Created ${escapeHtml(
            formatDate(problem.created_at)
        )}
                    </span>

                </div>

            </div>


            <div class="problem-actions">

                <button
                    class="
                        secondary-button
                        view-problem-button
                    "
                    type="button"
                    data-problem-id="${problem.id}"
                >
                    View Request
                </button>

            </div>
        `;

        problemList.appendChild(card);
    }

    const viewButtons = document.querySelectorAll(
        "[data-problem-id]"
    );

    for (const button of viewButtons) {
        button.addEventListener(
            "click",
            () => {
                openProblemDetail(
                    button.dataset.problemId
                );
            }
        );
    }
}


async function loadProblems() {
    problems = await getMyProblems();

    renderProblems();
}


async function openProblemDetail(problemId) {
    try {
        const problem = await getProblem(
            problemId
        );

        detailTitle.textContent =
            problem.title;

        problemDetailContent.innerHTML = `
            <section class="problem-detail-section">

                <div class="detail-status-row">

                    <span
                        class="
                            status-badge
                            ${getStatusClass(problem.status)}
                        "
                    >
                        ${escapeHtml(
            formatStatus(problem.status)
        )}
                    </span>

                    <span class="detail-id">
                        ${escapeHtml(problem.id)}
                    </span>

                </div>

            </section>


            <section class="problem-detail-section">

                <h3>
                    Development Need
                </h3>

                <p class="problem-detail-description">
                    ${escapeHtml(problem.description)}
                </p>

            </section>


            <section class="problem-detail-section">

                <h3>
                    Request Information
                </h3>

                <div class="detail-grid">

                    <div class="detail-item">

                        <span>
                            Location
                        </span>

                        <strong>
                            ${escapeHtml(
            getLocation(problem)
        )}
                        </strong>

                    </div>


                    <div class="detail-item">

                        <span>
                            Language
                        </span>

                        <strong>
                            ${escapeHtml(
            problem.language
        )}
                        </strong>

                    </div>


                    <div class="detail-item">

                        <span>
                            Created
                        </span>

                        <strong>
                            ${escapeHtml(
            formatDate(
                problem.created_at
            )
        )}
                        </strong>

                    </div>


                    <div class="detail-item">

                        <span>
                            Submitted
                        </span>

                        <strong>
                            ${escapeHtml(
            formatDate(
                problem.submitted_at
            )
        )}
                        </strong>

                    </div>

                </div>

            </section>
        `;

        problemModal.classList.remove(
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


async function saveComplaint({
    shouldSubmit,
}) {
    complaintError.textContent = "";

    setComplaintLoading(true);

    try {
        const payload = getComplaintPayload();

        validateComplaintPayload(
            payload
        );

        const problem = await createProblem(
            payload
        );

        if (shouldSubmit) {
            await submitProblem(
                problem.id
            );
        }

        closeComplaintModal();

        await loadProblems();

    } catch (error) {
        console.error(error);

        complaintError.textContent =
            error.data?.detail ||
            error.message ||
            "Unable to save request.";

    } finally {
        setComplaintLoading(false);
    }
}


async function handleLogout() {
    await logoutUser();

    window.location.href =
        "../index.html";
}


async function initializeClientPage() {
    try {
        const firebaseUser = await waitForAuth();

        if (!firebaseUser) {
            window.location.href =
                "../index.html";

            return;
        }

        currentUser = await getCurrentUser();

        if (
            currentUser.role !==
            USER_ROLES.CLIENT
        ) {
            window.location.href =
                "../index.html";

            return;
        }

        userEmail.textContent =
            currentUser.email ||
            currentUser.username ||
            "Citizen";

        await loadProblems();

        setPageReady();

    } catch (error) {
        console.error(error);

        await logoutUser();

        window.location.href =
            "../index.html";
    }
}


openComplaintButton.addEventListener(
    "click",
    openComplaintModal
);


closeComplaintButton.addEventListener(
    "click",
    closeComplaintModal
);


cancelComplaintButton.addEventListener(
    "click",
    closeComplaintModal
);


closeProblemButton.addEventListener(
    "click",
    closeProblemModal
);


logoutButton.addEventListener(
    "click",
    handleLogout
);


saveDraftButton.addEventListener(
    "click",
    () => {
        saveComplaint({
            shouldSubmit: false,
        });
    }
);


complaintForm.addEventListener(
    "submit",
    (event) => {
        event.preventDefault();

        saveComplaint({
            shouldSubmit: true,
        });
    }
);


complaintModal.addEventListener(
    "click",
    (event) => {
        if (
            event.target === complaintModal
        ) {
            closeComplaintModal();
        }
    }
);


problemModal.addEventListener(
    "click",
    (event) => {
        if (
            event.target === problemModal
        ) {
            closeProblemModal();
        }
    }
);


document.addEventListener(
    "keydown",
    (event) => {
        if (event.key !== "Escape") {
            return;
        }

        closeComplaintModal();

        closeProblemModal();
    }
);


initializeClientPage();