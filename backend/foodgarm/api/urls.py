from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserFollowView,
    UserFollowGetView
)


v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path(
        'users/subscriptions/',
        UserFollowGetView.as_view()
    ),
    path('users/<int:user_id>/subscribe/', UserFollowView.as_view()),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
