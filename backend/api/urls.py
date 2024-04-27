from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers
from users.views import UserView

router = routers.DefaultRouter()
router.register('users', UserView)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserView),
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
]
