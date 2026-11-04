import {
    Conversation,
    Message,
    Source,
    getConversations,
    createConversation,
    getConversationMessages,
    sendMessage,
    deleteConversation,
    updateConversationTitle,
} from "./api.js";

import {
    showNotification,
} from "./notifications.js";

import {
    logout,
} from "./auth.js";

let currentConversationId: number | null = null;

let conversations: Conversation[] = [];

let pendingDeleteConversationId: number | null = null;


const chatMessages = document.getElementById(
    "chat-messages"
) as HTMLElement;

const chatForm = document.getElementById(
    "chat-form"
) as HTMLFormElement;

const chatInput = document.getElementById(
    "chat-input"
) as HTMLTextAreaElement;

const newChatButton = document.getElementById(
    "new-chat-button"
) as HTMLButtonElement;

const chatHistory = document.querySelector(
    ".chat-history"
) as HTMLElement;

const chatHeader = document.querySelector(
    ".chat-header strong"
) as HTMLElement;

const chatUserButton = document.getElementById(
        "chat-user-button"
) as HTMLButtonElement;

const chatUserDropdown = document.getElementById(
        "chat-user-dropdown"
) as HTMLElement;

const logoutButton = document.getElementById(
        "logout-button"
) as HTMLButtonElement;

const chatUserName = document.querySelector(
        ".chat-user-name"
) as HTMLElement;

const chatUserEmail = document.querySelector(
        ".chat-user-email"
) as HTMLElement;

const chatMenuButton = document.getElementById(
    "chat-menu-button"
) as HTMLButtonElement;

const chatSidebar = document.querySelector(
    ".chat-sidebar"
) as HTMLElement;

const chatSidebarOverlay = document.getElementById(
    "chat-sidebar-overlay"
) as HTMLElement;

const deleteConversationModal = document.getElementById(
        "delete-conversation-modal"
    ) as HTMLElement;

const deleteConversationModalMessage = document.getElementById(
        "delete-conversation-modal-message"
    ) as HTMLElement;

const deleteConversationModalCancel = document.getElementById(
        "delete-conversation-modal-cancel"
    ) as HTMLButtonElement;

const deleteConversationModalConfirm = document.getElementById(
        "delete-conversation-modal-confirm"
    ) as HTMLButtonElement;

const deleteConversationModalOverlay = document.getElementById(
        "delete-conversation-modal-overlay"
    ) as HTMLElement;


export async function initializeChat(): Promise<void> {

    setupEventListeners();

    await loadConversations();
}


function setupEventListeners(): void {
    newChatButton.addEventListener(
        "click",
        handleNewConversation
    );

    chatForm.addEventListener(
        "submit",
        handleSubmit
    );

    chatUserButton.addEventListener(
        "click",
        toggleUserMenu
    );

    logoutButton.addEventListener(
        "click",
        handleLogout
    );

    document.addEventListener(
        "click",
        handleDocumentClick
    );

    chatMenuButton.addEventListener(
        "click",
        toggleMobileSidebar
    );

    chatSidebarOverlay.addEventListener(
        "click",
        closeMobileSidebar
    );

    deleteConversationModalCancel.addEventListener(
        "click",
        closeDeleteConversationModal
    );

    deleteConversationModalOverlay.addEventListener(
        "click",
        closeDeleteConversationModal
    );

    deleteConversationModalConfirm.addEventListener(
        "click",
        confirmDeleteConversation
    );

    setupChatInput();

}


async function loadConversations(): Promise<void> {

    conversations = await getConversations();

    renderConversationHistory();

    if (conversations.length > 0) {

        await selectConversation(
            conversations[0].id
        );

    } else {

        await createNewConversation();
    }
}


function renderConversationHistory(): void {
    chatHistory.innerHTML = "";

    const title =
        document.createElement("div");

    title.className =
        "chat-history-title";

    title.textContent =
        "Historial";

    chatHistory.appendChild(
        title
    );

    conversations.forEach(
        (conversation) => {
            const item =
                document.createElement("div");

            item.className =
                "chat-history-item-wrapper";

            const button =
                document.createElement("button");

            button.className =
                "chat-history-item";

            if (
                conversation.id ===
                currentConversationId
            ) {
                button.classList.add(
                    "active"
                );
            }

            button.type = "button";

            button.textContent =
                conversation.title;

            button.addEventListener(
                "click",
                async () => {
                    await selectConversation(
                        conversation.id
                    );
                }
            );

            const deleteButton =
                document.createElement("button");

            deleteButton.type = "button";

            deleteButton.className =
                "chat-history-delete";

            deleteButton.setAttribute(
                "aria-label",
                `Eliminar ${conversation.title}`
            );

            deleteButton.textContent =
                "×";

            deleteButton.addEventListener(
                "click",
                async (event) => {
                    event.stopPropagation();

                    await handleDeleteConversation(
                        conversation.id
                    );
                }
            );

            item.appendChild(
                button
            );

            item.appendChild(
                deleteButton
            );

            chatHistory.appendChild(
                item
            );
        }
    );
}

function handleDeleteConversation(
    conversationId: number
): void {

    const conversation =
        conversations.find(
            (item) =>
                item.id === conversationId
        );

    if (!conversation) {
        return;
    }

    pendingDeleteConversationId =
        conversationId;

    deleteConversationModalMessage.textContent =
        `¿Quieres eliminar la conversación "${conversation.title}"?`;

    deleteConversationModal.hidden =
        false;

    deleteConversationModalConfirm.focus();
}

function closeDeleteConversationModal(): void {

    deleteConversationModal.hidden =
        true;

    pendingDeleteConversationId =
        null;
}


async function confirmDeleteConversation(): Promise<void> {

    if (
        pendingDeleteConversationId ===
        null
    ) {
        return;
    }

    const conversationId =
        pendingDeleteConversationId;

    deleteConversationModalConfirm.disabled =
        true;

    deleteConversationModalConfirm.textContent =
        "Eliminando...";

    try {

        await deleteConversation(
            conversationId
        );

        conversations =
            conversations.filter(
                (item) =>
                    item.id !==
                    conversationId
            );

        closeDeleteConversationModal();

        if (
            currentConversationId ===
            conversationId
        ) {

            currentConversationId =
                null;

            if (
                conversations.length > 0
            ) {

                await selectConversation(
                    conversations[0].id
                );

            } else {

                await createNewConversation();
            }

            showNotification(
                "Conversación eliminada.",
                "success"
            );

            return;
        }

        renderConversationHistory();

        showNotification(
            "Conversación eliminada.",
            "success"
        );

    } catch (error) {

        console.error(
            "Error eliminando conversación:",
            error
        );

        closeDeleteConversationModal();

        showNotification(
            error instanceof Error
                ? error.message
                : "No se ha podido eliminar la conversación.",
            "error"
        );

    } finally {

        deleteConversationModalConfirm.disabled =
            false;

        deleteConversationModalConfirm.textContent =
            "Eliminar";
    }
}


async function selectConversation(
    conversationId: number
): Promise<void> {

    currentConversationId = conversationId;

    closeMobileSidebar();

    const conversation =
        conversations.find(
            (item) =>
                item.id === conversationId
        );

    if (!conversation) {
        return;
    }

    chatHeader.textContent =
        conversation.title;

    renderConversationHistory();

    const messages =
        await getConversationMessages(
            conversationId
        );

    renderMessages(messages);
}


async function createNewConversation(): Promise<void> {

    const conversation =
        await createConversation();

    conversations.unshift(
        conversation
    );

    await selectConversation(
        conversation.id
    );
}


async function handleNewConversation(): Promise<void> {
    try {
        await createNewConversation();
    } catch (error) {
        console.error(
            "Error creando conversación:",
            error
        );

        showNotification(
            error instanceof Error
                ? error.message
                : "No se ha podido crear la conversación.",
            "error"
        );
    }
}


async function handleSubmit(
    event: SubmitEvent
): Promise<void> {

    event.preventDefault();

    if (!currentConversationId) {
        return;
    }

    const content =
        chatInput.value.trim();

    if (!content) {
        return;
    }

    const isFirstMessage =
    chatMessages.querySelector(
        ".chat-message.user"
    ) === null;

    chatInput.value = "";

    autoResizeInput();

    addMessageToUI(
        {
            id: Date.now(),
            conversation_id:
                currentConversationId,
            role: "user",
            content,
            created_at:
                new Date().toISOString(),
            sources: [],
        },
        []
    );

    setLoading(true);

    try {

        const response =
            await sendMessage(
                currentConversationId,
                content
            );

        if (
            isFirstMessage &&
            currentConversationId !== null
        ) {
            try {

                await updateCurrentConversationTitle(
                    currentConversationId,
                    content
                );
            } catch (error) {
                console.error(
                    "Error actualizando título:",
                    error
                );
            }
        }

        addMessageToUI(
            response.assistant_message,
            response.sources
        );

        await refreshConversations();

    } catch (error) {

        console.error(
            "Error enviando mensaje:",
            error
        );

        addErrorMessage(
            error instanceof Error
                ? error.message
                : "No se ha podido enviar el mensaje."
        );

    } finally {

        setLoading(false);
    }
}


async function refreshConversations(): Promise<void> {

    conversations =
        await getConversations();

    renderConversationHistory();
}

function generateConversationTitle(
    message: string
): string {
    const title = message
        .trim()
        .replace(/\s+/g, " ");

    const maxLength = 50;

    if (title.length <= maxLength) {
        return title;
    }

    return `${title.substring(0, maxLength - 3)}...`;
}

async function updateCurrentConversationTitle(
    conversationId: number,
    firstMessage: string
): Promise<void> {
    const title =
        generateConversationTitle(
            firstMessage
        );

    const updatedConversation =
        await updateConversationTitle(
            conversationId,
            title
        );

    conversations =
        conversations.map(
            (conversation) =>
                conversation.id ===
                updatedConversation.id
                    ? updatedConversation
                    : conversation
        );

    renderConversationHistory();

    chatHeader.textContent =
        updatedConversation.title;
}


function renderMessages(
    messages: Message[]
): void {

    chatMessages.innerHTML = "";

    if (messages.length === 0) {

        renderWelcome();

        return;
    }

    messages.forEach(
        (message) => {

            addMessageToUI(
                message,
                message.sources ?? []
            );
        }
    );
}


function renderWelcome(): void {

    const welcome =
        document.createElement("div");

    welcome.className =
        "chat-welcome";

    welcome.innerHTML = `
        <div class="chat-welcome-icon">
            ✦
        </div>

        <h1>
            ¿En qué puedo ayudarte?
        </h1>

        <p>
            Pregunta sobre cualquiera de los
            documentos disponibles en DocuWise.
        </p>
    `;

    chatMessages.appendChild(
        welcome
    );
}


function addMessageToUI(
    message: Message,
    sources: Source[]
): void {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `chat-message ${message.role}`;

    const messageContentWrapper =
        document.createElement("div");

    messageContentWrapper.className =
        "chat-message-wrapper";

    const content =
        document.createElement("div");

    content.className =
        "chat-message-content";

    const messageText =
        document.createElement("div");

    messageText.className =
        "chat-message-text";

    renderMessageContent(
        messageText,
        message.content
    );

    content.appendChild(
        messageText
    );

    if (
        message.role === "assistant" &&
        sources.length > 0
    ) {

        const sourcesContainer =
            document.createElement("div");

        sourcesContainer.className =
            "chat-message-sources";

        const sourcesButton =
            document.createElement("button");

        sourcesButton.type =
            "button";

        sourcesButton.className =
            "chat-message-sources-toggle";

        sourcesButton.setAttribute(
            "aria-expanded",
            "false"
        );

        sourcesButton.innerHTML = `
            <span class="chat-message-sources-arrow">
                ▾
            </span>

            <span>
                Fuentes
            </span>
        `;

        const sourcesList =
            document.createElement("div");

        sourcesList.className =
            "chat-message-sources-list";

        sourcesList.hidden =
            true;

        sourcesList.style.display =
            "none";

        sources.forEach(
            (source) => {

                const sourceElement =
                    document.createElement("div");

                sourceElement.className =
                    "chat-message-source";

                sourceElement.textContent =
                    source.page_number === null
                        ? `📄 ${source.filename}`
                        : `📄 ${source.filename} — página ${source.page_number}`;

                sourcesList.appendChild(
                    sourceElement
                );
            }
        );

        sourcesButton.addEventListener(
            "click",
            () => {

                const isExpanded =
                    sourcesButton.getAttribute(
                        "aria-expanded"
                    ) === "true";

                sourcesButton.setAttribute(
                    "aria-expanded",
                    String(!isExpanded)
                );

                sourcesList.hidden =
                    isExpanded;

                sourcesList.style.display =
                    isExpanded
                        ? "none"
                        : "flex";

                const arrow =
                    sourcesButton.querySelector(
                        ".chat-message-sources-arrow"
                    );

                if (arrow) {

                    arrow.textContent =
                        isExpanded
                            ? "▾"
                            : "▴";
                }
            }
        );

        sourcesContainer.appendChild(
            sourcesButton
        );

        sourcesContainer.appendChild(
            sourcesList
        );

        content.appendChild(
            sourcesContainer
        );
    }

    messageContentWrapper.appendChild(
        content
    );

    messageElement.appendChild(
        messageContentWrapper
    );

    chatMessages.appendChild(
        messageElement
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}

function appendInlineMarkdown(
    container: HTMLElement,
    text: string
): void {
    const inlineMarkdownPattern =
        /(\*\*|__)(.+?)\1|`([^`]+)`|\*([^*\n]+)\*|_([^_\n]+)_/g;

    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while (
        (match = inlineMarkdownPattern.exec(text)) !== null
    ) {
        if (match.index > lastIndex) {
            container.appendChild(
                document.createTextNode(
                    text.slice(lastIndex, match.index)
                )
            );
        }

        if (match[3] !== undefined) {
            const code = document.createElement("code");
            code.textContent = match[3];
            container.appendChild(code);
        } else {
            const emphasis = document.createElement(
                match[1] !== undefined ? "strong" : "em"
            );
            const formattedText =
                match[2] ?? match[4] ?? match[5] ?? "";

            appendInlineMarkdown(
                emphasis,
                formattedText
            );
            container.appendChild(emphasis);
        }

        lastIndex = inlineMarkdownPattern.lastIndex;
    }

    if (lastIndex < text.length) {
        container.appendChild(
            document.createTextNode(text.slice(lastIndex))
        );
    }
}


function renderMessageContent(
    container: HTMLElement,
    text: string
): void {

    const lines =
        text.replace(/\r\n/g, "\n").split("\n");

    let currentList: HTMLOListElement | HTMLUListElement | null = null;
    let currentListType: "ordered" | "unordered" | null = null;

    function closeList(): void {
        currentList = null;
        currentListType = null;
    }

    lines.forEach(
        (line) => {

            const trimmed =
                line.trim();

            if (!trimmed) {

                closeList();

                const spacer =
                    document.createElement("div");

                spacer.className =
                    "message-line-break";

                container.appendChild(
                    spacer
                );

                return;
            }

            const orderedMatch =
                trimmed.match(
                    /^(\d+)[.)]\s+(.+)$/
                );

            const unorderedMatch =
                trimmed.match(
                    /^[-*]\s+(.+)$/
                );

            if (orderedMatch) {

                if (
                    currentListType !==
                    "ordered"
                ) {

                    closeList();

                    currentList =
                        document.createElement(
                            "ol"
                        );

                    currentListType =
                        "ordered";

                    currentList.className =
                        "message-list";

                    container.appendChild(
                        currentList
                    );
                }

                const item =
                    document.createElement("li");

                appendInlineMarkdown(
                    item,
                    orderedMatch[2]
                );

                if (currentList) {
                    currentList.appendChild(
                        item
                    );
                }

                return;
            }

            if (unorderedMatch) {

                if (
                    currentListType !==
                    "unordered"
                ) {

                    closeList();

                    currentList =
                        document.createElement(
                            "ul"
                        );

                    currentListType =
                        "unordered";

                    currentList.className =
                        "message-list";

                    container.appendChild(
                        currentList
                    );
                }

                const item =
                    document.createElement("li");

                appendInlineMarkdown(
                    item,
                    unorderedMatch[1]
                );

                if (currentList) {
                    currentList.appendChild(
                        item
                    );
                }

                return;
            }

            closeList();

            const paragraph =
                document.createElement("p");

            appendInlineMarkdown(
                paragraph,
                trimmed
            );

            container.appendChild(
                paragraph
            );
        }
    );
}


function addErrorMessage(
    message: string
): void {

    const errorElement =
        document.createElement("div");

    errorElement.className =
        "chat-message error";

    errorElement.textContent =
        message;

    chatMessages.appendChild(
        errorElement
    );
}


function setLoading(
    loading: boolean
): void {
    const sendButton =
        chatForm.querySelector(
            ".chat-send"
        ) as HTMLButtonElement;

    sendButton.disabled =
        loading;

    chatInput.disabled =
        loading;

    sendButton.textContent =
        loading
            ? "Enviando..."
            : "Enviar";

    const existingLoading =
        chatMessages.querySelector(
            ".chat-message.loading"
        );

    if (loading) {
        if (existingLoading) {
            return;
        }

        const loadingElement =
            document.createElement("div");

        loadingElement.className =
            "chat-message assistant loading";

        const content =
            document.createElement("div");

        content.className =
            "chat-message-content";

        content.innerHTML = `
            <span class="loading-text">
                DocuWise está pensando
            </span>

            <span class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </span>
        `;

        loadingElement.appendChild(
            content
        );

        chatMessages.appendChild(
            loadingElement
        );

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

        return;
    }

    if (existingLoading) {
        existingLoading.remove();
    }
}

function toggleUserMenu(): void {
    const isOpen =
        !chatUserDropdown.hidden;

    chatUserDropdown.hidden =
        isOpen;

    chatUserButton.setAttribute(
        "aria-expanded",
        String(!isOpen)
    );
}

function toggleMobileSidebar(): void {
    const isOpen =
        chatSidebar.classList.contains("open");

    if (isOpen) {
        closeMobileSidebar();
    } else {
        openMobileSidebar();
    }
}


function openMobileSidebar(): void {
    chatSidebar.classList.add("open");
    chatSidebarOverlay.classList.add("visible");

    chatMenuButton.setAttribute(
        "aria-expanded",
        "true"
    );
}


function closeMobileSidebar(): void {
    chatSidebar.classList.remove("open");
    chatSidebarOverlay.classList.remove("visible");

    chatMenuButton.setAttribute(
        "aria-expanded",
        "false"
    );
}

function handleDocumentClick(
    event: MouseEvent
): void {
    const target =
        event.target as Node;

    if (
        !chatUserButton.contains(target) &&
        !chatUserDropdown.contains(target)
    ) {
        chatUserDropdown.hidden =
            true;

        chatUserButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }
}

function handleLogout(): void {
    showNotification(
        "Cerrando sesión...",
        "info"
    );

    window.setTimeout(() => {
        logout();
    }, 300);
}

function setupChatInput(): void {
    chatInput.addEventListener(
        "keydown",
        async (event: KeyboardEvent) => {
            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();

                if (!chatInput.value.trim()) {
                    return;
                }

                chatForm.requestSubmit();
            }
        }
    );

    chatInput.addEventListener(
        "input",
        autoResizeInput
    );
}

function autoResizeInput(): void {

    chatInput.style.height = "0px";

    const newHeight =
        Math.min(
            chatInput.scrollHeight,
            200
        );

    chatInput.style.height =
        `${newHeight}px`;
}
