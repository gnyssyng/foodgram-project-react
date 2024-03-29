from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from django.views.generic import TemplateView
from djoser.views import TokenCreateView, TokenDestroyView
from api.views import TagViewSet
from users.views import UserMeView

router = routers.DefaultRouter()
# Роутер приложений
router.register(r'tags', TagViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/', include(router.urls)),
    path('api/users/me/', UserMeView.as_view()),
    path('api/', include('djoser.urls')),
    path('api/auth/token/login/', TokenCreateView.as_view()),
    path('api/auth/token/logout/', TokenDestroyView.as_view()),
]
