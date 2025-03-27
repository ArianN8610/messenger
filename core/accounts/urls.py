from django.urls import path
from .views import ProfileCompleteView, UpdateProfileView

app_name = 'accounts'

urlpatterns = [
    path('complete-profile/', ProfileCompleteView.as_view(), name='complete-profile'),
    path('update-profile/<int:pk>/', UpdateProfileView.as_view(), name='update-profile')
]
