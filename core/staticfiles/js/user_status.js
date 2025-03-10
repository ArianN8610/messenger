userStatusSocket.addEventListener('open', () => {
    sendOnlineStatus();
})

// Send online status when the user is on the site
function sendOnlineStatus() {
    if (userStatusSocket.readyState === WebSocket.OPEN) {
        userStatusSocket.send(JSON.stringify({type: 'online'}));
    }
}

// Send offline status when user leaves tab
function sendOfflineStatus() {
    if (userStatusSocket.readyState === WebSocket.OPEN) {
        userStatusSocket.send(JSON.stringify({type: 'offline'}));
    }
}

// Listening to browser events
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        sendOnlineStatus();  // Set online when the tab is activated
    } else {
        sendOfflineStatus(); // Set offline when the tab is disabled
    }
});

// When the site is closed, the user goes offline
window.addEventListener('beforeunload', () => {
    sendOfflineStatus();
});
