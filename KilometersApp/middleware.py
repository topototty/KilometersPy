import threading
from django.contrib.auth.models import AnonymousUser

_thread_locals = threading.local()

def get_current_user():
    """Retrieve the current user from thread-local storage."""
    user = getattr(_thread_locals, 'user', None)
    # Return None if the user is AnonymousUser
    if isinstance(user, AnonymousUser):
        return None
    return user

class CurrentUserMiddleware:
    """Middleware to store the current user in thread-local storage."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the user only if it's authenticated
        _thread_locals.user = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        return response
