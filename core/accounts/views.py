from django.shortcuts import redirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile
from .forms import ProfileCompleteForm


class ProfileCompleteView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileCompleteForm
    template_name = 'account/profile_complete.html'
    success_url = '/'

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user)
        if profile.exists():
            return redirect('/')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        profile_form = form.save(commit=False)
        profile_form.user = self.request.user
        profile_form.save()

        return super().form_valid(form)
