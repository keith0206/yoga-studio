from django.http import HttpResponse


class HealthCheckMiddleware:
    """Return /health/ before host validation so Fly checks never hit DisallowedHost."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health/" or request.path == "/health":
            return HttpResponse("ok")
        return self.get_response(request)
