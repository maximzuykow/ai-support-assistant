from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.webhooks.views import WebhookView


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health_check, name='health'),
    path('health/', health_check),
    path('webhooks/helpdesk', WebhookView.as_view(), name='helpdesk-webhook'),
    path('api/webhooks/', include('apps.webhooks.urls')),
    path('api/', include('apps.assistant.urls')),
    path('api/', include('apps.integrations.urls')),
]