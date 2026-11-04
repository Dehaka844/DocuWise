import { getCurrentUser } from "./api.js";
export function getAccessToken() {
    return localStorage.getItem("access_token");
}
export function isAuthenticated() {
    return getAccessToken() !== null;
}
export function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "./login.html";
}
export async function loadCurrentUser() {
    return getCurrentUser();
}
export async function requireAuthentication() {
    if (!isAuthenticated()) {
        window.location.href = "./login.html";
        throw new Error("Usuario no autenticado.");
    }
    try {
        return await loadCurrentUser();
    }
    catch {
        logout();
        throw new Error("Sesión no válida.");
    }
}
//# sourceMappingURL=auth.js.map