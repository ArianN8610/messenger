from django.urls import path
from .views import ProfileCompleteView

app_name = 'accounts'

urlpatterns = [
    path('complete-profile/', ProfileCompleteView.as_view(), name='complete-profile')
]
