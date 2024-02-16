import base64

from django.db import IntegrityError
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    IngredientRecipe,
    ShoppingCart,
    Tag
)
from users.models import User, Follow


class Base64ImageField(serializers.ImageField):
    """For images."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSignUpSerializer(UserCreateSerializer):
    """User registration."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )


class UserGetSerializer(UserSerializer):
    """User information."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists())


class RecipeBitSerializer(serializers.ModelSerializer):
    """Brief information about the recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowInfoSerializer(UserGetSerializer):
    """User follow information."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        recipes_limit = (
            self.context.get('request').query_params.get('recipes_limit'))
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                recipes = obj.recipes.all()
        return RecipeBitSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for follow/unfollowing from users."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, value):
        request = self.context.get('request')
        return UserFollowInfoSerializer(
            value.author, context={'request': request}
        ).data


class TagSerialiser(serializers.ModelSerializer):
    """Serializer for working with tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for working with ingredients."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Get information about ingredients."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientRecipe


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """To create ingredients."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Колличество индигриентов не может быть меньше 1.'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for obtaining recipe information."""

    tags = TagSerialiser(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def recipe_get(self, model, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return model.objects.filter(user=user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.recipe_get(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.recipe_get(ShoppingCart, obj)


class RecipeNotSafeMetodSerialaizer(serializers.ModelSerializer):
    """Serializer for create/updating a recipe."""

    ingredients = IngredientRecipeCreateSerializer(
        many=True, source='ingredientrecipes',
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['name', 'text'],
                message='Такой рецепт уже существует!'
            )
        ]

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время не должно быть меньше 1.'
            )
        return value

    def validate(self, attrs):
        ingredients = attrs.get('ingredientrecipes')
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы 1 ингредиент!'
            )
        unique_ingredients = []
        for ingredient in ingredients:
            try:
                ingredients = Ingredient.objects.get(
                    id=ingredient.get('id')
                )
            except ValueError:
                raise serializers.ValidationError(
                    'Такого индигриента не существует.'
                )
            if ingredients in unique_ingredients:
                raise serializers.ValidationError(
                    'Индигриенты должны быть уникальны.'
                )
            unique_ingredients.append(ingredients)
        return attrs

    def validate_tags(self, tags):
        unique_tags = []
        if not tags:
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы 1 тег!'
            )
        for tag in tags:
            if tag in unique_tags:
                raise serializers.ValidationError(
                    'Теги должны быть уникальны.'
                )
            unique_tags.append(tag)
        return tags

    def add_ingredients(self, ingredients, recipe):
        ingredient_list = []
        [ingredient_list.append(
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient.get('id')
                ),
                amount=ingredient.get('amount')
            )
        ) for ingredient in ingredients]
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        try:
            recipe = Recipe.objects.create(
                author=self.context.get('request').user,
                **validated_data
            )
            recipe.tags.set(tags)
            self.add_ingredients(ingredients, recipe)
            return recipe
        except IntegrityError:
            raise serializers.ValidationError(
                'Такой рецепт уже существует!'
            )

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, value):
        request = self.context.get('request')
        return RecipeSerializer(
            value,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Working with favorite recipes."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeBitSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Working with a shopping carts."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeBitSerializer(
            instance.recipe,
            context={'request': request}
        ).data
