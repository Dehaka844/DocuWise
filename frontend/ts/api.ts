const API_BASE_URL = "http://127.0.0.1:8000";

interface ApiRequestOptions {
    method?: string;
    body?: unknown;
}

async function apiRequest<T>(
    endpoint: string,
    options: ApiRequestOptions = {}
): Promise<T> {

    const token = localStorage.getItem("access_token");

    const isFormData = options.body instanceof FormData;
    const headers: HeadersInit = {};

    if (!isFormData) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            method: options.method ?? "GET",
            headers,
            body: options.body
                ? isFormData
                    ? options.body as FormData
                    : JSON.stringify(options.body)
                : undefined,
        }
    );

    if (!response.ok) {

        let detail =
            "Ha ocurrido un error.";

        try {

            const errorData =
                await response.json();

            if (
                typeof errorData.detail ===
                "string"
            ) {

                detail =
                    errorData.detail;

            } else if (
                Array.isArray(
                    errorData.detail
                )
            ) {

                detail =
                    errorData.detail
                        .map(
                            (
                                error: unknown
                            ) => {

                                if (
                                    typeof error ===
                                    "string"
                                ) {
                                    return error;
                                }

                                if (
                                    typeof error ===
                                    "object" &&
                                    error !== null &&
                                    "msg" in error
                                ) {
                                    return String(
                                        (
                                            error as {
                                                msg: unknown;
                                            }
                                        ).msg
                                    );
                                }

                                return String(error);
                            }
                        )
                        .join(". ");

            } else if (
                errorData.detail !==
                undefined
            ) {

                detail =
                    String(
                        errorData.detail
                    );
            }

        } catch {
            // No hacemos nada si la respuesta no contiene JSON.
        }

        throw new Error(detail);
    }

    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}


export interface Conversation {
    id: number;
    user_id: number;
    title: string;
    created_at: string;
    updated_at: string;
}


export interface Message {
    id: number;
    conversation_id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
    sources: Source[];
}


export interface Source {
    filename: string;
    page_number: number | null;
}


export interface CreateMessageResponse {
    user_message: Message;
    assistant_message: Message;
    sources: Source[];
    has_sufficient_context: boolean;
}


export interface RegisterRequest {
    name: string;
    email: string;
    password: string;
}


export interface LoginRequest {
    email: string;
    password: string;
}


export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: {
        id: number;
        name: string;
        email: string;
        is_active: boolean;
        created_at: string;
        updated_at: string;
    };
}


export interface AdminUser {
    id: number;
    name: string;
    email: string;
    role: "user" | "admin";
    is_active: boolean;
    departments: string[];
    created_at: string;
}


export interface AdminUserCreateRequest {
    name: string;
    email: string;
    password: string;
    departments: string[];
}


export interface UploadedDocument {
    filename: string;
    chunk_count: number;
    embedding_count: number;
    stored_points: number;
}


export async function getConversations(): Promise<Conversation[]> {
    return apiRequest<Conversation[]>(
        "/conversations/"
    );
}


export async function createConversation(): Promise<Conversation> {
    return apiRequest<Conversation>(
        "/conversations/",
        {
            method: "POST",
        }
    );
}


export async function getConversationMessages(
    conversationId: number
): Promise<Message[]> {

    return apiRequest<Message[]>(
        `/conversations/${conversationId}/messages`
    );
}


export async function sendMessage(
    conversationId: number,
    content: string,
    limit: number = 5
): Promise<CreateMessageResponse> {

    return apiRequest<CreateMessageResponse>(
        `/conversations/${conversationId}/messages`,
        {
            method: "POST",
            body: {
                content,
                limit,
            },
        }
    );
}


export async function deleteConversation(
    conversationId: number
): Promise<void> {

    await apiRequest<void>(
        `/conversations/${conversationId}`,
        {
            method: "DELETE",
        }
    );
}

export async function updateConversationTitle(
    conversationId: number,
    title: string
): Promise<Conversation> {
    return apiRequest<Conversation>(
        `/conversations/${conversationId}`,
        {
            method: "PATCH",
            body: { title },
        }
    );
}


export async function getCurrentUser<T>(): Promise<T> {
    return apiRequest<T>("/auth/me");
}

export async function register(
    data: RegisterRequest
): Promise<void> {

    await apiRequest<void>(
        "/auth/register",
        {
            method: "POST",
            body: data,
        }
    );
}


export async function login(
    data: LoginRequest
): Promise<LoginResponse> {

    return apiRequest<LoginResponse>(
        "/auth/login",
        {
            method: "POST",
            body: data,
        }
    );
}


export async function getAdminUsers(): Promise<AdminUser[]> {
    return apiRequest<AdminUser[]>("/admin/users/");
}


export async function createAdminUser(
    data: AdminUserCreateRequest
): Promise<AdminUser> {
    return apiRequest<AdminUser>("/admin/users/", {
        method: "POST",
        body: data,
    });
}


export async function updateAdminUser(
    userId: number,
    changes: {
        role?: "user" | "admin";
        is_active?: boolean;
        departments?: string[];
    }
): Promise<AdminUser> {
    return apiRequest<AdminUser>(`/admin/users/${userId}`, {
        method: "PATCH",
        body: changes,
    });
}


export async function deleteAdminUser(userId: number): Promise<void> {
    await apiRequest<void>(`/admin/users/${userId}`, {
        method: "DELETE",
    });
}


export async function uploadDocument(
    file: File,
    metadata: {
        visibility: "all" | "departments" | "personal";
        allowed_departments: string[];
        owner_user_id?: number;
    }
): Promise<UploadedDocument> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("visibility", metadata.visibility);
    metadata.allowed_departments.forEach((department) => {
        formData.append("allowed_departments", department);
    });
    if (metadata.owner_user_id !== undefined) {
        formData.append("owner_user_id", String(metadata.owner_user_id));
    }

    return apiRequest<UploadedDocument>("/documents/", {
        method: "POST",
        body: formData,
    });
}


export async function deleteDocument(filename: string): Promise<void> {
    await apiRequest<void>(
        `/documents/?filename=${encodeURIComponent(filename)}`,
        { method: "DELETE" }
    );
}
