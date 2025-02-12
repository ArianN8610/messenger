from django.views.generic import ListView

from .models import PrivateChat


class IndexView(ListView):
    model = PrivateChat
    template_name = 'messenger/index.html'
    context_object_name = 'chats'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # General search result
        if q := self.request.GET.get('q'):
            context['global_search_results'] = PrivateChat.objects.search(self.request.user, q, True)

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

        return chats
