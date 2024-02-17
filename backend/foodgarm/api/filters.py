from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, Ingredient
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)
        model = Recipe

    def get_is_favorited(self, queryset, name, value):
        if not value or self.request.user.is_anonymous:
            return queryset
        return queryset.filter(favorite_recipe__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value or self.request.user.is_anonymous:
            return queryset
        return queryset.filter(shopping_carts__user=self.request.user)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
