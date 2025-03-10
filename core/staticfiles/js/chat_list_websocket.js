const chatListSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat-list/'
);

chatListSocket.addEventListener('message', e => {
    document.body.dispatchEvent(new Event("updateChatList"));
});
