from django.views.generic import ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404

from . import models
from accounts.models import User

from decouple import config


def get_users_ids(chats, user):
    """Get other users id to display status in frontend"""
    users_ids = []
    for user_chat in chats:
        if other_user := user_chat.get_other_user(user):
            users_ids.append(other_user.id)

    return users_ids


class IndexView(ListView):
    model = models.PrivateChat
    template_name = 'messenger/index.html'
    context_object_name = 'chats'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # General search result
        if q := self.request.GET.get('q'):
            context['global_search_results'] = models.PrivateChat.objects.search(self.request.user, q, True)

        return context | {'users_ids': get_users_ids(self.get_queryset(), self.request.user)}

    def get_queryset(self):
        user = self.request.user
        chats = self.model.objects.for_user(user)

        # Search result
        if q := self.request.GET.get('q'):
            chats = self.model.objects.search(user, q)

        self.model.update_chat_values(chats, self.request.user)

        return chats


class PrivateChatView(ListView):
    model = models.Message
    template_name = 'messenger/private-chat.html'
    context_object_name = 'messages'
    paginate_by = 50

    def get_template_names(self):
        """Use a different template for AJAX (HTMX) requests"""
        if self.request.htmx or self.request.GET.get('ajax'):
            return 'messenger/message-object.html'
        return self.template_name

    def get_context_data(self, **kwargs):
        # Get current chat
        chat = get_object_or_404(models.PrivateChat, id=self.kwargs['chat_id'])

        if not chat.has_user_view_permission(self.request.user):
            raise Http404

        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        chats = models.PrivateChat.objects.for_user(current_user)
        # Search result
        if q := self.request.GET.get('q'):
            chats = models.PrivateChat.objects.search(self.request.user, q)
        models.PrivateChat.update_chat_values(chats, current_user)

        other_user = chat.get_other_user(current_user)
        chat.other_user = other_user.profile if other_user else None

        # CKEditor env
        ckeditor_license_key = config("CKEDITOR_LICENSE_KEY")

        # General search result
        if q := self.request.GET.get('q'):
            context['global_search_results'] = models.PrivateChat.objects.search(self.request.user, q, True)

        messages = self.get_queryset()
        # Find the page with the first unseen message
        first_unseen_message = messages.filter(seen_at__isnull=True).exclude(sender=self.request.user).last()
        unseen_page_number = None

        if first_unseen_message:
            message_index = list(messages).index(first_unseen_message)
            unseen_page_number = (message_index // self.paginate_by) + 1

        return context | {'chats': chats, 'chat': chat, 'ckeditor_license_key': ckeditor_license_key,
                          'unseen_page_number': unseen_page_number, 'users_ids': get_users_ids(chats, current_user),
                          'first_unseen_id': first_unseen_message.id if first_unseen_message else None}

    def get_queryset(self):
        messages = self.model.objects.filter(chat=self.kwargs['chat_id']).order_by("-sent_at")

        # Add "new_day" field to specify the start of a new day
        prev_date = None
        for message in reversed(messages):
            message.new_day = prev_date != message.sent_at.date()
            prev_date = message.sent_at.date()

        return messages


class ChatListView(ListView):
    model = models.PrivateChat
    template_name = 'messenger/sidebar.html'
    context_object_name = 'chats'

    def get_queryset(self):
        user = self.request.user
        chats = self.model.objects.for_user(user)

        # Search result
        if q := self.request.GET.get('q'):
            chats = self.model.objects.search(user, q)

        self.model.update_chat_values(chats, user)
        return chats

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        chat_id = self.request.GET.get('chat-id')
        context['chat_id'] = int(chat_id) if chat_id else chat_id

        # General search result
        if q := self.request.GET.get('q'):
            context['global_search_results'] = self.model.objects.search(self.request.user, q, True)

        return context


class StartChatView(View):
    def get(self, request, *args, **kwargs):
        return redirect('messenger:index')

    def post(self, request, *args, **kwargs):
        other_user_id = request.POST.get('other_user')
        other_user = get_object_or_404(User, id=other_user_id)

        chat, created = models.PrivateChat.objects.get_or_create(user1=request.user, user2=other_user)
        return redirect(chat.get_absolute_url())  # Redirect to chat page
