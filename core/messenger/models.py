from django.db import models
from django.shortcuts import reverse
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity

from accounts.models import Profile, User


class PrivateChatManager(models.Manager):
    def for_user(self, user):
        """Returns all chats the user has"""
        return self.filter(models.Q(user1=user) | models.Q(user2=user)).annotate(
            last_message_time=models.Subquery(
                Message.objects.filter(chat=models.OuterRef('pk'))
                .order_by('-sent_at')  # Order messages by newest
                .values('sent_at')[:1]  # Get the time of the last message
            )
        ).order_by('-last_message_time')  # Order chats by latest message

    def search(self, user, query, global_search=False):
        """Returns chats that match query"""

        if not global_search:  # Search for chats in which the user has participated
            # Get receiver for each chat
            chats = self.get_queryset().annotate(
                other_user=models.Case(
                    models.When(user1=user, then=models.F("user2")),
                    models.When(user2=user, then=models.F("user1")),
                    default=models.Value(None),
                ),
                other_user_username=models.Subquery(
                    User.objects.filter(id=models.OuterRef("other_user")).values("username")[:1]
                ),
                full_name=models.Subquery(
                    Profile.objects.filter(user=models.OuterRef("other_user"))
                    .annotate(
                        name=Concat("first_name", models.Value(" "), "last_name", output_field=models.CharField())
                    )
                    .values("name")[:1]
                )
            )

            # Search only on receiver
            return chats.annotate(
                similarity=TrigramSimilarity("other_user_username", query) +
                           TrigramSimilarity("full_name", query)
            ).filter(similarity__gt=0.4).order_by("-similarity")  # Show only relevant results
        else:  # Search for chats in which the user hasn't participated
            # Get the chats the user is in
            existing_chat_users = User.objects.filter(
                models.Q(chats_initiated__user2=user) | models.Q(chats_received__user1=user)
            )

            users = User.objects.annotate(
                full_name=models.Subquery(
                    Profile.objects.filter(user=models.OuterRef("id"))
                    .annotate(
                        name=Concat("first_name", models.Value(" "), "last_name", output_field=models.CharField())
                    )
                    .values("name")[:1]
                )
            )

            # Search results
            return users.annotate(
                similarity=TrigramSimilarity("username", query) +
                           TrigramSimilarity("full_name", query)
            ).filter(
                similarity__gt=0.4,
            ).exclude(
                id__in=existing_chat_users.values_list("id", flat=True)  # Exclude users who already have chat with user
            ).exclude(
                id=user.id  # Exclude the user from the results
            ).order_by("-similarity")


class PrivateChat(models.Model):
    user1 = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='chats_initiated', null=True)
    user2 = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='chats_received', null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = PrivateChatManager()  # To use custom manager

    class Meta:
        unique_together = ('user1', 'user2')  # Both users only have one private chat

    def __str__(self):
        return f'{self.user1.username} & {self.user2.username}'

    def get_absolute_url(self):
        return reverse('messenger:private-chat', kwargs={'chat_id': self.pk})

    def count_unread_messages(self, current_user):
        other_user = self.get_other_user(current_user)
        return self.messages.all().filter(sender=other_user, seen_at__isnull=True).count()  # Get all unread messages

    def get_other_user(self, current_user):
        """Check who the current user is in this chat and return the other user"""
        return self.user2 if self.user1 == current_user else self.user1

    def get_last_message(self):
        return self.messages.all().order_by('-sent_at').first()

    @staticmethod
    def update_chat_values(chats, current_user):
        """Add other user and unread messages for each chat"""
        for chat in chats:
            chat.other_user = chat.get_other_user(current_user).profile
            chat.unread_messages = chat.count_unread_messages(current_user)


class Message(models.Model):
    sender = models.ForeignKey('accounts.User', related_name='messages', on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages')

    content = models.TextField()
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    seen_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.sender.username} -> ({self.chat.__str__()})'
