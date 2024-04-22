from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserView

router = routers.DefaultRouter()
router.register(r'users', CustomUserView)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/', include(router.urls)),
    path('api/users/', CustomUserView),
    path('api/', include('djoser.urls')),
    path('api/auth/token/login/', TokenCreateView.as_view()),
    path('api/auth/token/logout/', TokenDestroyView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
