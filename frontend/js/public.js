import {
    API_BASE_URL,
} from "./config.js";


const approvedProjectCount =
    document.getElementById(
        "approvedProjectCount"
    );

const totalInvestment =
    document.getElementById(
        "totalInvestment"
    );

const peopleImpacted =
    document.getElementById(
        "peopleImpacted"
    );

const projectSearch =
    document.getElementById(
        "projectSearch"
    );

const categoryFilter =
    document.getElementById(
        "categoryFilter"
    );

const publicError =
    document.getElementById(
        "publicError"
    );

const publicLoading =
    document.getElementById(
        "publicLoading"
    );

const projectList =
    document.getElementById(
        "projectList"
    );

const emptyProjects =
    document.getElementById(
        "emptyProjects"
    );

const projectModal =
    document.getElementById(
        "projectModal"
    );

const closeProjectButton =
    document.getElementById(
        "closeProjectButton"
    );

const modalProjectTitle =
    document.getElementById(
        "modalProjectTitle"
    );

const projectDetail =
    document.getElementById(
        "projectDetail"
    );


let projects = [];


function escapeHtml(value) {
    const element =
        document.createElement("div");

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


function formatNumber(value) {
    return new Intl.NumberFormat(
        "en-IN"
    ).format(
        Number(value || 0)
    );
}


function formatStatus(status) {
    return String(status || "")
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(
            /\b\w/g,
            (character) =>
                character.toUpperCase()
        );
}


function buildLocation(project) {
    return [
        project.locality,
        project.ward,
        project.district,
        project.state,
    ]
        .filter(Boolean)
        .join(", ");
}


function showError(message) {
    publicError.textContent = message;

    publicError.classList.remove(
        "hidden"
    );
}


function clearError() {
    publicError.textContent = "";

    publicError.classList.add(
        "hidden"
    );
}


async function getPublicProjects() {
    const response = await fetch(
        `${API_BASE_URL}/intelligence/public/projects/`
    );

    let data = null;

    try {
        data = await response.json();

    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(
            data?.detail ||
            "Failed to load public projects."
        );
    }

    return data;
}


async function getPublicProject(
    proposalId
) {
    const response = await fetch(
        `${API_BASE_URL}/intelligence/public/projects/${proposalId}/`
    );

    let data = null;

    try {
        data = await response.json();

    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(
            data?.detail ||
            "Failed to load project."
        );
    }

    return data;
}


function updateSummary() {
    approvedProjectCount.textContent =
        formatNumber(
            projects.length
        );


    const investment = projects.reduce(
        (total, project) =>
            total +
            Number(
                project.budget || 0
            ),
        0
    );

    totalInvestment.textContent =
        formatCurrency(
            investment
        );


    const impacted = projects.reduce(
        (total, project) =>
            total +
            Number(
                project
                    .estimated_affected_population ||
                0
            ),
        0
    );

    peopleImpacted.textContent =
        formatNumber(
            impacted
        );
}


function populateCategories() {
    const categories = [
        ...new Set(
            projects
                .map(
                    (project) =>
                        project.category
                )
                .filter(Boolean)
        ),
    ].sort();


    categoryFilter.innerHTML = `
        <option value="">
            All categories
        </option>
    `;


    for (const category of categories) {
        const option =
            document.createElement(
                "option"
            );

        option.value = category;

        option.textContent = category;

        categoryFilter.appendChild(
            option
        );
    }
}


function getFilteredProjects() {
    const searchValue =
        projectSearch.value
            .trim()
            .toLowerCase();

    const selectedCategory =
        categoryFilter.value;


    return projects.filter(
        (project) => {
            const searchableText = [
                project.title,
                project.summary,
                project.category,
                project.locality,
                project.ward,
                project.district,
                project.state,
                project.solution,
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();


            const matchesSearch =
                !searchValue ||
                searchableText.includes(
                    searchValue
                );


            const matchesCategory =
                !selectedCategory ||
                project.category ===
                selectedCategory;


            return (
                matchesSearch &&
                matchesCategory
            );
        }
    );
}


function renderProjects() {
    const filteredProjects =
        getFilteredProjects();


    projectList.innerHTML = "";


    if (!filteredProjects.length) {
        emptyProjects.classList.remove(
            "hidden"
        );

        return;
    }


    emptyProjects.classList.add(
        "hidden"
    );


    for (
        const project of filteredProjects
    ) {
        const card =
            document.createElement(
                "article"
            );

        card.className = "project-card";


        const location =
            buildLocation(project);


        card.innerHTML = `
            <div class="project-card-topline">

                <span class="project-category">
                    ${escapeHtml(
            project.category
        )}
                </span>

                <span class="project-status">
                    ${escapeHtml(
            formatStatus(
                project.status
            )
        )}
                </span>

            </div>


            <h3>
                ${escapeHtml(
            project.title
        )}
            </h3>


            <p class="project-summary">
                ${escapeHtml(
            project.summary
        )}
            </p>


            <div class="project-location">
                ${location
                ? escapeHtml(location)
                : "Location not specified"
            }
            </div>


            <div class="project-metrics">

                <div class="project-metric">

                    <span>
                        Priority
                    </span>

                    <strong>
                        ${escapeHtml(
                project.priority_score
            )} / 100
                    </strong>

                </div>


                <div class="project-metric">

                    <span>
                        People Impacted
                    </span>

                    <strong>
                        ${formatNumber(
                project
                    .estimated_affected_population
            )}
                    </strong>

                </div>


                <div class="project-metric">

                    <span>
                        Approved Budget
                    </span>

                    <strong>
                        ${formatCurrency(
                project.budget
            )}
                    </strong>

                </div>

            </div>


            <div class="project-card-action">

                <button
                    class="secondary-button"
                    type="button"
                    data-project-id="${project.id}"
                >
                    View Project
                </button>

            </div>
        `;


        projectList.appendChild(
            card
        );
    }


    const projectButtons =
        document.querySelectorAll(
            "[data-project-id]"
        );


    for (
        const button of projectButtons
    ) {
        button.addEventListener(
            "click",
            () => {
                openProject(
                    button.dataset.projectId
                );
            }
        );
    }
}


async function openProject(
    proposalId
) {
    try {
        const project =
            await getPublicProject(
                proposalId
            );


        modalProjectTitle.textContent =
            project.title;


        const location =
            buildLocation(project);


        projectDetail.innerHTML = `
            <div class="project-detail-grid">

                <div class="project-stat">

                    <span>
                        Priority Score
                    </span>

                    <strong>
                        ${escapeHtml(
            project.priority_score
        )} / 100
                    </strong>

                </div>


                <div class="project-stat">

                    <span>
                        Estimated Impact
                    </span>

                    <strong>
                        ${formatNumber(
            project
                .estimated_affected_population
        )}
                        people
                    </strong>

                </div>


                <div class="project-stat">

                    <span>
                        Approved Budget
                    </span>

                    <strong>
                        ${formatCurrency(
            project.budget
        )}
                    </strong>

                </div>

            </div>


            <section class="project-section">

                <h3>
                    Development Need
                </h3>

                <p>
                    ${escapeHtml(
            project.summary
        )}
                </p>

            </section>


            <section class="project-section">

                <h3>
                    Location
                </h3>

                <p>
                    ${location
                ? escapeHtml(
                    location
                )
                : "Location not specified"
            }
                </p>

            </section>


            <section class="project-section">

                <h3>
                    Approved Development Solution
                </h3>

                <div class="solution-box">

                    <p>
                        ${escapeHtml(
                project.solution
            )}
                    </p>

                </div>

            </section>


            <section class="project-section">

                <h3>
                    Public Investment
                </h3>

                <p>
                    <strong>
                        ${formatCurrency(
                project.budget
            )}
                    </strong>
                </p>

            </section>


            <section class="project-section">

                <h3>
                    Approval Status
                </h3>

                <p>
                    <strong>
                        ${escapeHtml(
                formatStatus(
                    project.status
                )
            )}
                    </strong>
                </p>

            </section>
        `;


        projectModal.classList.remove(
            "hidden"
        );

    } catch (error) {
        console.error(error);

        showError(
            error.message
        );
    }
}


function closeProjectModal() {
    projectModal.classList.add(
        "hidden"
    );
}


async function initializePublicPage() {
    clearError();

    publicLoading.classList.remove(
        "hidden"
    );

    projectList.classList.add(
        "hidden"
    );


    try {
        projects =
            await getPublicProjects();

        updateSummary();

        populateCategories();

        renderProjects();

        projectList.classList.remove(
            "hidden"
        );

    } catch (error) {
        console.error(error);

        showError(
            error.message
        );

    } finally {
        publicLoading.classList.add(
            "hidden"
        );
    }
}


projectSearch.addEventListener(
    "input",
    renderProjects
);


categoryFilter.addEventListener(
    "change",
    renderProjects
);


closeProjectButton.addEventListener(
    "click",
    closeProjectModal
);


projectModal.addEventListener(
    "click",
    (event) => {
        if (
            event.target === projectModal
        ) {
            closeProjectModal();
        }
    }
);


document.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Escape"
        ) {
            closeProjectModal();
        }
    }
);


initializePublicPage();