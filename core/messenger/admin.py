from django.contrib import admin
from .models import PrivateChat, Message


@admin.register(PrivateChat)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    search_fields = ('user1__email', 'user1__username', 'user2__email', 'user2__username')
    ordering = ('-created_at',)
    autocomplete_fields = ('user1', 'user2')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat', 'seen_at', 'sent_at')
    search_fields = ('sender__email', 'sender__username')
    ordering = ('-sent_at',)
    autocomplete_fields = ('sender', 'chat')
