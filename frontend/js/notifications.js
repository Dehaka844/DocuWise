export function showNotification(message, type = "info") {
    const containerId = "notification-container";
    let container = document.getElementById(containerId);
    if (!container) {
        container =
            document.createElement("div");
        container.id =
            containerId;
        container.className =
            "notification-container";
        document.body.appendChild(container);
    }
    const notification = document.createElement("div");
    notification.className =
        `notification notification-${type}`;
    const messageElement = document.createElement("span");
    messageElement.className =
        "notification-message";
    messageElement.textContent =
        message;
    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className =
        "notification-close";
    closeButton.setAttribute("aria-label", "Cerrar notificación");
    closeButton.textContent = "×";
    closeButton.addEventListener("click", () => {
        removeNotification(notification);
    });
    notification.appendChild(messageElement);
    notification.appendChild(closeButton);
    container.appendChild(notification);
    requestAnimationFrame(() => {
        notification.classList.add("visible");
    });
    window.setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}
function removeNotification(notification) {
    notification.classList.remove("visible");
    window.setTimeout(() => {
        notification.remove();
    }, 300);
}
//# sourceMappingURL=notifications.js.map