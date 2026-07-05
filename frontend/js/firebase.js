import { initializeApp } from
    "https://www.gstatic.com/firebasejs/12.2.1/firebase-app.js";

import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
} from
    "https://www.gstatic.com/firebasejs/12.2.1/firebase-auth.js";

import { firebaseConfig } from "./config.js";


const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);


export async function registerUser(email, password) {
    const credential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
    );

    return credential.user;
}


export async function loginUser(email, password) {
    const credential = await signInWithEmailAndPassword(
        auth,
        email,
        password
    );

    return credential.user;
}


export async function logoutUser() {
    await signOut(auth);
}


export async function getFirebaseToken() {
    const user = auth.currentUser;

    if (!user) {
        throw new Error("User is not authenticated.");
    }

    return await user.getIdToken();
}


export function waitForAuth() {
    return new Promise((resolve) => {
        const unsubscribe = onAuthStateChanged(
            auth,
            (user) => {
                unsubscribe();
                resolve(user);
            }
        );
    });
}