from django.http import JsonResponse
from django.conf import settings


def health_check(request):
    response = dict(
        status="healthy",
        version=settings.VERSION,
        debug=settings.DEBUG,
        message="Service is up and running",
    )
    return JsonResponse(response, status=200)
