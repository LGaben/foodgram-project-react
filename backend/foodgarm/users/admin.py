from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'email',
                    'role',
                    'first_name',
                    'last_name')
    search_fields = ('username', 'email', 'first_name',)
    empty_value_display = '-empty-'


@admin.register(Follow)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    empty_value_display = '-empty-'
