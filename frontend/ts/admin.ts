import {
    AdminUser,
    createAdminUser,
    deleteAdminUser,
    deleteDocument,
    getAdminUsers,
    updateAdminUser,
    uploadDocument,
} from "./api.js";
import { requireAuthentication, logout } from "./auth.js";
import { showNotification } from "./notifications.js";

type PendingAction =
    | { type: "user"; user: AdminUser }
    | { type: "document"; filename: string }
    | null;

const DEPARTMENTS = [
    { code: "rrhh", label: "Recursos humanos" },
    { code: "tecnico", label: "Técnico" },
    { code: "marketing", label: "Marketing" },
] as const;

let users: AdminUser[] = [];
let currentUserId: number | null = null;
let pendingAction: PendingAction = null;

const usersPanel = document.getElementById("users-panel") as HTMLElement;
const documentsPanel = document.getElementById("documents-panel") as HTMLElement;
const usersTab = document.getElementById("users-tab") as HTMLButtonElement;
const documentsTab = document.getElementById("documents-tab") as HTMLButtonElement;
const usersTableBody = document.getElementById("users-table-body") as HTMLElement;
const createUserForm = document.getElementById("create-user-form") as HTMLFormElement;
const uploadDocumentForm = document.getElementById("upload-document-form") as HTMLFormElement;
const deleteDocumentForm = document.getElementById("delete-document-form") as HTMLFormElement;
const confirmModal = document.getElementById("admin-confirm-modal") as HTMLElement;
const confirmMessage = document.getElementById("admin-confirm-message") as HTMLElement;
const confirmAccept = document.getElementById("admin-confirm-accept") as HTMLButtonElement;


async function initializeAdminPage(): Promise<void> {
    try {
        const user = await requireAuthentication();

        if (user.role !== "admin") {
            window.location.replace("./chat.html");
            return;
        }

        currentUserId = user.id;
        document.getElementById("admin-user-label")!.textContent = user.name;
        setupEventListeners();
        await loadUsers();
    } catch (error) {
        showNotification(
            error instanceof Error ? error.message : "No se ha podido abrir la administración.",
            "error"
        );
    }
}


function setupEventListeners(): void {
    usersTab.addEventListener("click", () => setActiveTab("users"));
    documentsTab.addEventListener("click", () => setActiveTab("documents"));

    document.getElementById("show-create-user-button")!
        .addEventListener("click", () => {
            createUserForm.hidden = false;
            createUserForm.querySelector<HTMLInputElement>("[name='name']")?.focus();
        });

    document.getElementById("hide-create-user-button")!
        .addEventListener("click", hideCreateUserForm);
    document.getElementById("cancel-create-user-button")!
        .addEventListener("click", hideCreateUserForm);
    createUserForm.addEventListener("submit", handleCreateUser);
    uploadDocumentForm.addEventListener("submit", handleUploadDocument);
    deleteDocumentForm.addEventListener("submit", handleRequestDeleteDocument);
    document.getElementById("document-visibility")!
        .addEventListener("change", updateDocumentAccessFields);

    document.getElementById("admin-logout-button")!
        .addEventListener("click", logout);
    document.getElementById("admin-confirm-cancel")!
        .addEventListener("click", closeConfirmModal);
    document.getElementById("admin-confirm-backdrop")!
        .addEventListener("click", closeConfirmModal);
    confirmAccept.addEventListener("click", handleConfirmAction);
}


function setActiveTab(tab: "users" | "documents"): void {
    const showUsers = tab === "users";
    usersTab.classList.toggle("active", showUsers);
    documentsTab.classList.toggle("active", !showUsers);
    usersTab.setAttribute("aria-selected", String(showUsers));
    documentsTab.setAttribute("aria-selected", String(!showUsers));
    usersPanel.hidden = !showUsers;
    documentsPanel.hidden = showUsers;
}


async function loadUsers(): Promise<void> {
    users = await getAdminUsers();
    renderUsers();
    renderStats();
    renderDocumentOwners();
}


function renderDocumentOwners(): void {
    const select = document.getElementById("document-owner") as HTMLSelectElement;
    select.replaceChildren(new Option("Selecciona un usuario", ""));
    users.forEach((user) => {
        if (!user.is_active) return;
        const label = `${user.name} — ${user.email}`;
        select.add(new Option(label, String(user.id)));
    });
}


function updateDocumentAccessFields(): void {
    const visibility = (document.getElementById("document-visibility") as HTMLSelectElement).value;
    document.getElementById("document-departments-group")!.hidden = visibility === "all";
    document.getElementById("document-owner-group")!.hidden = visibility !== "personal";
}


function renderStats(): void {
    document.getElementById("total-users-stat")!.textContent = String(users.length);
    document.getElementById("active-users-stat")!.textContent = String(
        users.filter((user) => user.is_active).length
    );
    document.getElementById("active-admins-stat")!.textContent = String(
        users.filter((user) => user.is_active && user.role === "admin").length
    );
}


function renderUsers(): void {
    usersTableBody.replaceChildren();

    if (users.length === 0) {
        usersTableBody.append(createMessageRow("No hay usuarios registrados."));
        return;
    }

    users.forEach((user) => {
        const row = document.createElement("tr");
        const identityCell = document.createElement("td");
        identityCell.className = "admin-user-identity";

        const name = document.createElement("strong");
        name.textContent = user.name;
        const email = document.createElement("span");
        email.textContent = user.email;
        identityCell.append(name, email);

        const roleCell = document.createElement("td");
        const roleSelect = document.createElement("select");
        roleSelect.className = "admin-select";
        roleSelect.setAttribute("aria-label", `Rol de ${user.name}`);
        roleSelect.add(new Option("Usuario", "user"));
        roleSelect.add(new Option("Administrador", "admin"));
        roleSelect.value = user.role;
        roleSelect.addEventListener("change", () => {
            void updateUser(user, { role: roleSelect.value as "user" | "admin" });
        });
        roleCell.appendChild(roleSelect);

        const departmentsCell = document.createElement("td");
        const departmentOptions = document.createElement("div");
        departmentOptions.className = "admin-row-departments";
        DEPARTMENTS.forEach((department) => {
            const label = document.createElement("label");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = user.departments.includes(department.code);
            checkbox.disabled = user.id === currentUserId;
            checkbox.dataset.department = department.code;
            checkbox.setAttribute(
                "aria-label",
                `${department.label} para ${user.name}`
            );
            checkbox.addEventListener("change", () => {
                const updatedDepartments = Array.from(
                    departmentOptions.querySelectorAll<HTMLInputElement>("input:checked")
                ).map((candidate) => candidate.dataset.department!);
                void updateUser(user, { departments: updatedDepartments });
            });
            label.append(checkbox, document.createTextNode(department.label));
            departmentOptions.appendChild(label);
        });
        departmentsCell.appendChild(departmentOptions);

        const statusCell = document.createElement("td");
        const statusBadge = document.createElement("span");
        statusBadge.className = `admin-status ${user.is_active ? "is-active" : "is-inactive"}`;
        statusBadge.textContent = user.is_active ? "Activa" : "Inactiva";
        statusCell.appendChild(statusBadge);

        const createdCell = document.createElement("td");
        createdCell.className = "admin-date-cell";
        createdCell.textContent = new Intl.DateTimeFormat("es-ES", {
            dateStyle: "medium",
        }).format(new Date(user.created_at));

        const actionsCell = document.createElement("td");
        actionsCell.className = "admin-actions-cell";
        const statusButton = document.createElement("button");
        statusButton.className = "admin-text-button";
        statusButton.type = "button";
        statusButton.textContent = user.is_active ? "Desactivar" : "Activar";
        statusButton.disabled = user.id === currentUserId && user.is_active;
        statusButton.title = statusButton.disabled
            ? "No puedes desactivar tu propia cuenta"
            : `${user.is_active ? "Desactivar" : "Activar"} cuenta`;
        statusButton.addEventListener("click", () => {
            void updateUser(user, { is_active: !user.is_active });
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "admin-text-button danger-text";
        deleteButton.type = "button";
        deleteButton.textContent = "Eliminar";
        deleteButton.disabled = user.id === currentUserId;
        deleteButton.title = deleteButton.disabled
            ? "No puedes eliminar tu propia cuenta"
            : "Eliminar usuario";
        deleteButton.addEventListener("click", () => openUserDeleteConfirmation(user));
        actionsCell.append(statusButton, deleteButton);

        row.append(identityCell, roleCell, departmentsCell, statusCell, createdCell, actionsCell);
        usersTableBody.appendChild(row);
    });
}


function createMessageRow(message: string): HTMLTableRowElement {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.className = "admin-table-message";
    cell.colSpan = 6;
    cell.textContent = message;
    row.appendChild(cell);
    return row;
}


async function updateUser(
    user: AdminUser,
    changes: {
        role?: "user" | "admin";
        is_active?: boolean;
        departments?: string[];
    }
): Promise<void> {
    try {
        await updateAdminUser(user.id, changes);
        await loadUsers();
        showNotification("Usuario actualizado.", "success");
    } catch (error) {
        await loadUsers();
        showNotification(
            error instanceof Error ? error.message : "No se ha podido actualizar el usuario.",
            "error"
        );
    }
}


async function handleCreateUser(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const formData = new FormData(createUserForm);
    const submit = document.getElementById("create-user-submit") as HTMLButtonElement;
    submit.disabled = true;
    submit.textContent = "Creando…";

    try {
        await createAdminUser({
            name: String(formData.get("name") ?? "").trim(),
            email: String(formData.get("email") ?? "").trim(),
            password: String(formData.get("password") ?? ""),
            departments: formData.getAll("departments").map(String),
        });
        createUserForm.reset();
        hideCreateUserForm();
        await loadUsers();
        showNotification("Usuario creado. Se ha asignado el rol de usuario.", "success");
    } catch (error) {
        showNotification(
            error instanceof Error ? error.message : "No se ha podido crear el usuario.",
            "error"
        );
    } finally {
        submit.disabled = false;
        submit.textContent = "Crear cuenta";
    }
}


function hideCreateUserForm(): void {
    createUserForm.hidden = true;
}


async function handleUploadDocument(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const fileInput = document.getElementById("document-file") as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (!file) return;

    const submit = document.getElementById("upload-document-submit") as HTMLButtonElement;
    const result = document.getElementById("upload-document-result") as HTMLElement;
    submit.disabled = true;
    submit.textContent = "Procesando…";
    result.textContent = "";

    try {
        const formData = new FormData(uploadDocumentForm);
        const visibility = String(formData.get("visibility")) as "all" | "departments" | "personal";
        const allowedDepartments = formData.getAll("allowed_departments").map(String);
        const ownerValue = String(formData.get("owner_user_id") ?? "");
        if (visibility === "departments" && allowedDepartments.length === 0) {
            throw new Error("Selecciona al menos un departamento autorizado.");
        }
        if (visibility === "personal" && !ownerValue) {
            throw new Error("Selecciona el usuario propietario del documento.");
        }
        const uploaded = await uploadDocument(file, {
            visibility,
            allowed_departments: allowedDepartments,
            owner_user_id: ownerValue ? Number(ownerValue) : undefined,
        });
        result.textContent = `${uploaded.filename}: ${uploaded.stored_points} fragmentos indexados.`;
        uploadDocumentForm.reset();
        showNotification("Documento subido e indexado.", "success");
    } catch (error) {
        showNotification(
            error instanceof Error ? error.message : "No se ha podido subir el documento.",
            "error"
        );
    } finally {
        submit.disabled = false;
        submit.textContent = "Subir e indexar";
    }
}


function handleRequestDeleteDocument(event: SubmitEvent): void {
    event.preventDefault();
    const filename = (document.getElementById("delete-document-filename") as HTMLInputElement)
        .value.trim();
    if (!filename) return;

    pendingAction = { type: "document", filename };
    openConfirmModal(
        "Eliminar documento",
        `Se eliminarán de Qdrant todos los fragmentos de “${filename}”. Esta acción no se puede deshacer.`,
        "Eliminar"
    );
}


function openUserDeleteConfirmation(user: AdminUser): void {
    pendingAction = { type: "user", user };
    openConfirmModal(
        "Eliminar usuario",
        `¿Quieres eliminar la cuenta de ${user.name}? También se borrarán sus conversaciones y mensajes.`,
        "Eliminar usuario"
    );
}


function openConfirmModal(title: string, message: string, actionLabel: string): void {
    document.getElementById("admin-confirm-title")!.textContent = title;
    confirmMessage.textContent = message;
    confirmAccept.textContent = actionLabel;
    confirmModal.hidden = false;
    confirmAccept.focus();
}


function closeConfirmModal(): void {
    confirmModal.hidden = true;
    pendingAction = null;
}


async function handleConfirmAction(): Promise<void> {
    if (!pendingAction) return;
    const action = pendingAction;
    confirmAccept.disabled = true;
    confirmAccept.textContent = "Procesando…";

    try {
        if (action.type === "document") {
            await deleteDocument(action.filename);
            deleteDocumentForm.reset();
            showNotification("Solicitud de borrado completada.", "success");
        } else {
            await deleteAdminUser(action.user.id);
            await loadUsers();
            showNotification("Usuario eliminado.", "success");
        }
        closeConfirmModal();
    } catch (error) {
        showNotification(
            error instanceof Error ? error.message : "No se ha podido completar la acción.",
            "error"
        );
    } finally {
        confirmAccept.disabled = false;
        confirmAccept.textContent = action.type === "document" ? "Eliminar" : "Eliminar usuario";
    }
}


void initializeAdminPage();
