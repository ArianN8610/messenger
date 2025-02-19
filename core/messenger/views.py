from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from . import models


class IndexView(ListView):
    model = models.PrivateChat
    template_name = 'messenger/index.html'
    context_object_name = 'chats'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # General search result
        if q := self.request.GET.get('q'):
            context['global_search_results'] = models.PrivateChat.objects.search(self.request.user, q, True)

        return context

    def get_queryset(self):
        user = self.request.user
        chats = self.model.objects.for_user(user)

        # Search result
        if q := self.request.GET.get('q'):
            chats = self.model.objects.search(user, q)

        # Get other user for each chat
        for chat in chats:
            chat.other_user = chat.get_other_user(user).profile
            chat.unread_messages = chat.count_unread_messages(self.request.user)

        return chats


class PrivateChatView(ListView):
    model = models.Message
    template_name = 'messenger/private-chat.html'
    context_object_name = 'messages'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        chats = models.PrivateChat.objects.for_user(self.request.user)
        # Get other user and unread_messages for each chat
        for chat in chats:
            chat.other_user = chat.get_other_user(self.request.user).profile
            chat.unread_messages = chat.count_unread_messages(self.request.user)

        # Get current chat
        chat = get_object_or_404(models.PrivateChat, id=self.kwargs['chat_id'])
        chat.other_user = chat.get_other_user(self.request.user).profile

        return context | {'chats': chats, 'chat': chat}

    def get_queryset(self):
        return self.model.objects.filter(chat=self.kwargs['chat_id']).order_by("sent_at")
