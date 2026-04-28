from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список URL, доступных без авторизации
        allowed_paths = [reverse('login'), reverse('register'), reverse('home')]
        
        if not request.session.get('access_token') and request.path not in allowed_paths:
            return redirect('login')

        response = self.get_response(request)
        return response