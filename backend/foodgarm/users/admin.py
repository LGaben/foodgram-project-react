from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow


@admin.register(User)
class UserProfileAdmin(UserAdmin):
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
