from django.urls import path
from . import views

app_name = 'messenger'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('private-chat/<int:chat_id>/', views.PrivateChatView.as_view(), name='private-chat'),
    path('chat-list/', views.ChatListView.as_view(), name='chat-list'),
    path('start-chat/', views.StartChatView.as_view(), name='start-chat'),
]
