export const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const firebaseConfig = {
    apiKey: "<firebase_api>",
    authDomain: "<firebase_auth_domain>",
    projectId: "<firebase_project_id>",
    storageBucket: "<firebase_project_bucket>",
    messagingSenderId: "<firebase_id>",
    appId: "<firebase_app_id>",
    measurementId: "<firebase_measurement_id>"
};


export const ROUTES = {
    LOGIN: "../index.html",
    CLIENT: "./client.html",
    MP: "./mp.html",
    PUBLIC: "./public.html",
};


export const USER_ROLES = {
    CLIENT: "CLIENT",
    MANAGEMENT: "MANAGEMENT",
    MP: "MP",
    ADMIN: "ADMIN",
};
