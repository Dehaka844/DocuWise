import { requireAuthentication, } from "./auth.js";
import { initializeChat, } from "./chat.js";
import { showNotification, } from "./notifications.js";
async function initializeChatPage() {
    try {
        const user = await requireAuthentication();
        const userElement = document.querySelector(".chat-user");
        const userNameElement = document.querySelector(".chat-user-name");
        const userEmailElement = document.querySelector(".chat-user-email");
        if (userElement) {
            userElement.textContent =
                user.name;
        }
        if (userNameElement) {
            userNameElement.textContent =
                user.name;
        }
        if (userEmailElement) {
            userEmailElement.textContent =
                user.email;
        }
        const adminLink = document.getElementById("chat-admin-link");
        if (adminLink && user.role === "admin") {
            adminLink.hidden = false;
        }
        await initializeChat();
    }
    catch (error) {
        console.error("Error inicializando DocuWise:", error);
        showNotification(error instanceof Error
            ? error.message
            : "No se ha podido inicializar DocuWise.", "error");
    }
}
const chatMessages = document.getElementById("chat-messages");
if (chatMessages) {
    initializeChatPage();
}
//# sourceMappingURL=main.js.map