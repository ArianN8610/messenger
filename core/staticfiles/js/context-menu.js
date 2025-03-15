// Select the context menu wrapper and messages box
const contextMenu = document.querySelector('.wrapper'),
    messagesBox = document.getElementById('messages-box');
let messageTarget;

// Define icons for context menu items
const itemsIcon = {
    reply: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" /></svg>`,
    edit: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" /></svg>`,
    copy: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" /></svg>`,
    forward: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="m15 15 6-6m0 0-6-6m6 6H9a6 6 0 0 0 0 12h3" /></svg>`,
    delete: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" /></svg>`,
}

// Function to convert a string to title case
function toTitleCase(str) {
    return str
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function get_message(element) {
    // Traverse up the DOM tree to find the element with id starting with 'message-'
    while (element && element !== document.body) {
        if (element.id && element.id.startsWith('message-')) {
            break;
        }
        element = element.parentElement;
    }

    return element;
}

// Function to update the context menu items based on the target element
function updateContextMenu(element) {
    element = get_message(element);

    // Define context menu items based on the class of the element
    let contextMenuItems;
    if (element.classList.contains('chat-end')) {
        contextMenuItems = ['reply', 'edit', 'copy', 'forward', 'delete']
    } else {
        contextMenuItems = ['reply', 'copy', 'forward']
    }

    // Generate HTML for context menu items
    let contextInnerHTML = ``;
    contextMenuItems.forEach(i => {
        contextInnerHTML += `<li>
                <a id="context-menu-${i}">
                    ${itemsIcon[i]}
                    <span>${toTitleCase(i)}</span>
                </a>
            </li>`;
    })

    return contextInnerHTML;
}

function copyFormattedText(element) {
    // Create a ClipboardItem object to copy text in HTML format
    const clipboardData = new ClipboardItem({
        "text/html": new Blob([element.innerHTML], { type: "text/html" }),
        "text/plain": new Blob([element.innerText], { type: "text/plain" })
    });

    navigator.clipboard.write([clipboardData]).catch(err => {
        console.error("Copy failed:", err);
    });
}

// Add contextmenu event listener to the messages box
messagesBox.addEventListener('contextmenu', e => {
    e.preventDefault();
    // Update the context menu content
    contextMenu.innerHTML = updateContextMenu(e.target);

    // Calculate the position of the context menu
    let x = e.clientX, y = e.clientY,
    winWidth = messagesBox.offsetWidth,
    winHeight = messagesBox.offsetHeight,
    cmWidth = contextMenu.offsetWidth,
    cmHeight = contextMenu.offsetHeight;

    // Adjust the position if the context menu goes out of the viewport
    x = x > winWidth - cmWidth ? x - cmWidth - 5 : x + 5;
    y = y > winHeight - cmHeight ? y - cmHeight - 5 : y + 5;

    // Set the position of the context menu
    contextMenu.style.left = `${x}px`;
    contextMenu.style.top = `${y}px`;
    // Show the context menu with animation
    contextMenu.classList.remove('invisible', 'opacity-0', 'scale-90');
    contextMenu.classList.add('opacity-100', 'scale-100');

    // Save the message that was clicked on
    messageTarget = get_message(e.target);
});

// Hide the context menu on click
document.addEventListener('click', () => {
    contextMenu.classList.remove('opacity-100', 'scale-100');
    contextMenu.classList.add('opacity-0', 'scale-90', 'invisible');
});

// Reset the context menu on window resize
window.addEventListener('resize', () => {
    contextMenu.style.left = '0px';
    contextMenu.style.top = '0px';
    contextMenu.classList.remove('opacity-100', 'scale-100');
    contextMenu.classList.add('opacity-0', 'scale-90', 'invisible');
});

// Hide the context menu on scrolling
messagesBox.addEventListener('scroll', () => {
    contextMenu.classList.remove('opacity-100', 'scale-100');
    contextMenu.classList.add('opacity-0', 'scale-90', 'invisible');
});

contextMenu.addEventListener('click', e => {
    const copyBtn = e.target.closest('#context-menu-copy');
    
    if (copyBtn) {
        const messageText = messageTarget.querySelector('div.chat-bubble');

        // Copy the text to clipboard
        copyFormattedText(messageText);
    }
});
