from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'openapi',
        get_schema_view(
            permission_classes=[AllowAny],
        ),
        name="openapi-schema",
    ),
    path(
        'api/docs/',
        TemplateView.as_view(
            template_name='redoc.html',
            extra_context={'schema_url': 'openapi-schema'}
        ),
        name='redoc'
    ),
    path('api/', include('api.urls'))
]
if settings.DEBUG is True:
    urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
