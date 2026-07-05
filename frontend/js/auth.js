import {
    loginUser,
    registerUser,
    waitForAuth,
} from "./firebase.js";

import {
    getCurrentUser,
} from "./api.js";

import {
    USER_ROLES,
} from "./config.js";


const authForm = document.getElementById(
    "authForm"
);

const emailInput = document.getElementById(
    "email"
);

const passwordInput = document.getElementById(
    "password"
);

const authTitle = document.getElementById(
    "authTitle"
);

const authSubtitle = document.getElementById(
    "authSubtitle"
);

const authSubmit = document.getElementById(
    "authSubmit"
);

const authError = document.getElementById(
    "authError"
);

const switchText = document.getElementById(
    "switchText"
);

const switchModeButton = document.getElementById(
    "switchMode"
);


let isRegisterMode = false;


function setLoading(isLoading) {
    authSubmit.disabled = isLoading;

    authSubmit.textContent = isLoading
        ? "Please wait..."
        : isRegisterMode
            ? "Create Account"
            : "Sign In";
}


function showError(message) {
    authError.textContent = message;
}


function clearError() {
    authError.textContent = "";
}


function updateAuthMode() {
    clearError();

    if (isRegisterMode) {
        authTitle.textContent = "Create your account";

        authSubtitle.textContent =
            "Join JanMitra and raise development requests.";

        authSubmit.textContent = "Create Account";

        switchText.textContent =
            "Already have an account?";

        switchModeButton.textContent =
            "Sign in";

        passwordInput.autocomplete =
            "new-password";

        return;
    }

    authTitle.textContent = "Welcome back";

    authSubtitle.textContent =
        "Sign in to submit and track your development requests.";

    authSubmit.textContent = "Sign In";

    switchText.textContent =
        "New to JanMitra?";

    switchModeButton.textContent =
        "Create account";

    passwordInput.autocomplete =
        "current-password";
}


function redirectByRole(user) {
    switch (user.role) {
        case USER_ROLES.CLIENT:
            window.location.href =
                "./pages/client.html";

            break;

        case USER_ROLES.MP:
            window.location.href =
                "./pages/mp.html";

            break;

        case USER_ROLES.ADMIN:
        case USER_ROLES.MANAGEMENT:
            showError(
                "Management dashboard is not available yet."
            );

            break;

        default:
            showError(
                "Unknown account role."
            );
    }
}


async function loadAuthenticatedUser() {
    try {
        const user = await getCurrentUser();

        redirectByRole(user);

    } catch (error) {
        showError(
            error.data?.detail ||
            error.message
        );
    }
}


switchModeButton.addEventListener(
    "click",
    () => {
        isRegisterMode = !isRegisterMode;

        updateAuthMode();
    }
);


authForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        clearError();
        setLoading(true);

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        try {
            if (isRegisterMode) {
                await registerUser(
                    email,
                    password
                );

            } else {
                await loginUser(
                    email,
                    password
                );
            }

            await loadAuthenticatedUser();

        } catch (error) {
            console.error(error);

            showError(
                error.data?.detail ||
                error.message ||
                "Authentication failed."
            );

        } finally {
            setLoading(false);
        }
    }
);


async function initializeAuthPage() {
    const firebaseUser = await waitForAuth();

    if (!firebaseUser) {
        return;
    }

    setLoading(true);

    await loadAuthenticatedUser();

    setLoading(false);
}


updateAuthMode();

initializeAuthPage();