from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingCart, Tag, IngredientRecipe
)
from users.models import User, Follow
from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeNotSafeMetodSerialaizer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerialiser,
    UserFollowInfoSerializer,
    UserFollowSerializer
)
from .mixins import ListViewSet


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Getting information about tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Getting information about ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, IngredientSearchFilter)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Working with recipes."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeNotSafeMetodSerialaizer

    def recipe_post_delite(self, request, pk, model, serialiser_class):
        if request.method == 'POST':
            serializer = serialiser_class(
                data={
                    'user': request.user.id,
                    'recipe': get_object_or_404(Recipe, id=pk).id,
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not model.objects.filter(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.filter(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated,]
    )
    def favorite(self, request, pk):
        return self.recipe_post_delite(
            request,
            pk,
            Favorite,
            FavoriteSerializer
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated,]
    )
    def shopping_cart(self, request, pk):
        return self.recipe_post_delite(
            request,
            pk,
            ShoppingCart,
            ShoppingCartSerializer
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated,]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(
                ingredient.get('ingredient__name'),
                ingredient.get('ingredient_amount'),
                ingredient.get('ingredient__measurement_unit')
            )
        ) for ingredient in ingredients]
        response = HttpResponse(
            'Ваш список покупок:\n' + '\n'.join(file_list),
            content_type='text/plain'
        )
        return response


class UserFollowView(APIView):
    """Creating/deleting a subscription for a user."""

    def post(self, request, user_id):
        serializer = UserFollowSerializer(
            data={
                'user': request.user.id,
                'author': get_object_or_404(User, id=user_id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        if not Follow.objects.filter(
            user=request.user,
            author=get_object_or_404(User, id=user_id)
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get(
            user=request.user.id,
            author=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFollowGetView(ListViewSet):
    """Getting user subscriptions."""

    serializer_class = UserFollowInfoSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
