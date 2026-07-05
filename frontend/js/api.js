import { API_BASE_URL } from "./config.js";
import { getFirebaseToken } from "./firebase.js";


async function apiRequest(
    endpoint,
    options = {}
) {
    const token = await getFirebaseToken();

    const headers = {
        Authorization: `Bearer ${token}`,
        ...options.headers,
    };

    if (
        options.body &&
        !(options.body instanceof FormData)
    ) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers,
        }
    );

    let data = null;

    if (response.status !== 204) {
        const contentType = response.headers.get(
            "content-type"
        );

        if (
            contentType &&
            contentType.includes("application/json")
        ) {
            data = await response.json();
        }
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


export function getCurrentUser() {
    return apiRequest(
        "/auth/me/",
        {
            method: "GET",
        }
    );
}


export function getMyProblems() {
    return apiRequest(
        "/problems/",
        {
            method: "GET",
        }
    );
}


export function getProblem(problemId) {
    return apiRequest(
        `/problems/${problemId}/`,
        {
            method: "GET",
        }
    );
}


export function createProblem(problemData) {
    return apiRequest(
        "/problems/",
        {
            method: "POST",
            body: JSON.stringify(problemData),
        }
    );
}


export function updateProblem(
    problemId,
    problemData
) {
    return apiRequest(
        `/problems/${problemId}/`,
        {
            method: "PATCH",
            body: JSON.stringify(problemData),
        }
    );
}


export function submitProblem(problemId) {
    return apiRequest(
        `/problems/${problemId}/submit/`,
        {
            method: "POST",
        }
    );
}


export function deleteProblemMedia(
    problemId,
    mediaId
) {
    return apiRequest(
        `/problems/${problemId}/media/${mediaId}/`,
        {
            method: "DELETE",
        }
    );
}