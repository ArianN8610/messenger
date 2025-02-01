from django.db import models


class PrivateChat(models.Model):
    user1 = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='chats_initiated', null=True)
    user2 = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='chats_received', null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Both users only have one private chat

    def __str__(self):
        return f'{self.user1.username} & {self.user2.username}'


class Message(models.Model):
    sender = models.ForeignKey('accounts.User', related_name='messages', on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages')

    content = models.TextField()
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    seen_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sender.username} -> ({self.chat.__str__()})'
