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
        // Check if the request has the header to scroll to the bottom (for new messages)
        const requestEvent = e.detail.requestConfig.triggeringEvent.type;
        if (requestEvent === "updateMessagesBox") {
            // Ensure scrolling to the very bottom after rendering
            requestAnimationFrame(() => {
                chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
            });
        } else {
            const newScrollHeight = chatBox.scrollHeight;
            // Maintain scroll position after loading previous messages
            requestAnimationFrame(() => {
                chatBox.scrollTop = newScrollHeight - oldScrollHeight;
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
