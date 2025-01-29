from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed on each request before the view (or next middleware) is called
        if not request.user.is_authenticated and not request.path.startswith('/accounts/'):
            return redirect('account_login')  # Redirect to login page
        return self.get_response(request)
