const API_BASE_URL = "http://127.0.0.1:8000";
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");
    const isFormData = options.body instanceof FormData;
    const headers = {};
    if (!isFormData) {
        headers["Content-Type"] = "application/json";
    }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: options.method ?? "GET",
        headers,
        body: options.body
            ? isFormData
                ? options.body
                : JSON.stringify(options.body)
            : undefined,
    });
    if (!response.ok) {
        let detail = "Ha ocurrido un error.";
        try {
            const errorData = await response.json();
            if (typeof errorData.detail ===
                "string") {
                detail =
                    errorData.detail;
            }
            else if (Array.isArray(errorData.detail)) {
                detail =
                    errorData.detail
                        .map((error) => {
                        if (typeof error ===
                            "string") {
                            return error;
                        }
                        if (typeof error ===
                            "object" &&
                            error !== null &&
                            "msg" in error) {
                            return String(error.msg);
                        }
                        return String(error);
                    })
                        .join(". ");
            }
            else if (errorData.detail !==
                undefined) {
                detail =
                    String(errorData.detail);
            }
        }
        catch {
            // No hacemos nada si la respuesta no contiene JSON.
        }
        throw new Error(detail);
    }
    if (response.status === 204) {
        return undefined;
    }
    return response.json();
}
export async function getConversations() {
    return apiRequest("/conversations/");
}
export async function createConversation() {
    return apiRequest("/conversations/", {
        method: "POST",
    });
}
export async function getConversationMessages(conversationId) {
    return apiRequest(`/conversations/${conversationId}/messages`);
}
export async function sendMessage(conversationId, content, limit = 5) {
    return apiRequest(`/conversations/${conversationId}/messages`, {
        method: "POST",
        body: {
            content,
            limit,
        },
    });
}
export async function deleteConversation(conversationId) {
    await apiRequest(`/conversations/${conversationId}`, {
        method: "DELETE",
    });
}
export async function updateConversationTitle(conversationId, title) {
    return apiRequest(`/conversations/${conversationId}`, {
        method: "PATCH",
        body: { title },
    });
}
export async function getCurrentUser() {
    return apiRequest("/auth/me");
}
export async function register(data) {
    await apiRequest("/auth/register", {
        method: "POST",
        body: data,
    });
}
export async function login(data) {
    return apiRequest("/auth/login", {
        method: "POST",
        body: data,
    });
}
export async function getAdminUsers() {
    return apiRequest("/admin/users/");
}
export async function createAdminUser(data) {
    return apiRequest("/admin/users/", {
        method: "POST",
        body: data,
    });
}
export async function updateAdminUser(userId, changes) {
    return apiRequest(`/admin/users/${userId}`, {
        method: "PATCH",
        body: changes,
    });
}
export async function deleteAdminUser(userId) {
    await apiRequest(`/admin/users/${userId}`, {
        method: "DELETE",
    });
}
export async function uploadDocument(file, metadata) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("visibility", metadata.visibility);
    metadata.allowed_departments.forEach((department) => {
        formData.append("allowed_departments", department);
    });
    if (metadata.owner_user_id !== undefined) {
        formData.append("owner_user_id", String(metadata.owner_user_id));
    }
    return apiRequest("/documents/", {
        method: "POST",
        body: formData,
    });
}
export async function deleteDocument(filename) {
    await apiRequest(`/documents/?filename=${encodeURIComponent(filename)}`, { method: "DELETE" });
}
//# sourceMappingURL=api.js.map