from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed on each request before the view (or next middleware) is called
        if not request.user.is_authenticated and not request.path.startswith('/accounts/'):
            return redirect('account_login')  # Redirect to login page
        return self.get_response(request)


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        complete_profile_url = reverse('accounts:complete-profile')
        profile = getattr(request.user, 'profile', None)  # Get user profile

        if (request.user.is_authenticated and not profile and
                request.path != complete_profile_url and not request.path.startswith("/__reload__/")):
            return redirect(complete_profile_url)

        return self.get_response(request)
