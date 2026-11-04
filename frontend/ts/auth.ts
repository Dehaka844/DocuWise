import { getCurrentUser } from "./api.js";


export interface User {
    id: number;
    name: string;
    email: string;
    role: "user" | "admin";
    is_active: boolean;
    created_at: string;
    updated_at: string;
}


export function getAccessToken(): string | null {
    return localStorage.getItem("access_token");
}


export function isAuthenticated(): boolean {
    return getAccessToken() !== null;
}


export function logout(): void {
    localStorage.removeItem("access_token");
    window.location.href = "./login.html";
}


export async function loadCurrentUser(): Promise<User> {
    return getCurrentUser<User>();
}


export async function requireAuthentication(): Promise<User> {

    if (!isAuthenticated()) {
        window.location.href = "./login.html";
        throw new Error("Usuario no autenticado.");
    }

    try {
        return await loadCurrentUser();
    } catch {
        logout();
        throw new Error("Sesión no válida.");
    }
}
