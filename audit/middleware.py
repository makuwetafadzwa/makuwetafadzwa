"""Thread-local storage of the current request's user and IP, so model
signals can stamp audit entries with the actor without having to thread
the request through every save() call."""
import threading


_storage = threading.local()


def get_current_user():
    return getattr(_storage, "user", None)


def get_current_ip():
    return getattr(_storage, "ip", None)


def set_current_user(user):
    _storage.user = user


def set_current_ip(ip):
    _storage.ip = ip


def clear():
    _storage.user = None
    _storage.ip = None


def _client_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        set_current_ip(_client_ip(request))
        try:
            response = self.get_response(request)
        finally:
            clear()
        return response
