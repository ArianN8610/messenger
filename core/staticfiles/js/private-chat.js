const chatBox = document.getElementById("messages-box");
let oldScrollHeight = 0;

// Save the scroll height before loading previous messages
document.body.addEventListener("htmx:beforeRequest", (e) => {
    if (e.detail.elt.classList.contains("loading-box")) {
        oldScrollHeight = chatBox.scrollHeight;
    }
});

// Handle after HTMX content swap
document.body.addEventListener("htmx:afterSwap", (e) => {
    const triggeredElement = e.detail.elt;

    if (triggeredElement.id === "messages-box") {
        const triggeringEvent = e.detail.requestConfig?.triggeringEvent;
        const requestEvent = triggeringEvent?.type;

        if (requestEvent === "intersect") {
            const newScrollHeight = chatBox.scrollHeight;
            // Maintain scroll position after loading previous messages
            requestAnimationFrame(() => {
                chatBox.scrollTop = newScrollHeight - oldScrollHeight;
            });
        }

        // Check if the request has the header to scroll to the bottom (for new messages)
        if (requestEvent === "updateMessagesBox" && websocket_type === "message") {
            // Ensure scrolling to the very bottom after rendering
            requestAnimationFrame(() => {
                chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
            });
        }
    }
});

// Remove the loading element after loading previous messages
document.body.addEventListener("htmx:afterRequest", (e) => {
    const triggeredElement = e.detail.elt;
    if (triggeredElement.classList.contains("loading-box")) {
        triggeredElement.remove();
    }
});

// Display pinned messages
document.getElementById("pin-checkbox").addEventListener('change', e => {
    const messagesBox = document.getElementById("messages-box");
    const baseUrl = messagesBox.getAttribute("data-base-url");

    if (!baseUrl) return;

    const newUrl = e.target.checked ? `${baseUrl}?pin=1` : baseUrl;
    messagesBox.setAttribute("hx-get", newUrl);

    // Force a new HTMX request without relying on hx-trigger
    htmx.ajax('GET', newUrl, {
        target: "#messages-box",
        swap: "innerHTML"
    });

    setTimeout(() => {
        messagesBox.scrollTo({ top: messagesBox.scrollHeight, behavior: 'smooth' });
    }, 1000);
})
