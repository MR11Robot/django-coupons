# decorators.py
from django.http import JsonResponse
from django.conf import settings

def key_required(view_func):
    def wrapper(request, *args, **kwargs):
        sent_token = request.headers.get('X-API-KEY')
        if sent_token != settings.SITE_API_KEY:
            return JsonResponse({"error": "Invalid API KEY"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper