from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = [
        (USER, 'user'),
        (ADMIN, 'admin')
    ]

    username = models.CharField(
        verbose_name='Пользователь',
        max_length=150,
        unique=True,
        help_text=(
            'Не больше 150 символов.'
            'Только буквы, цифры и @/./+/-/_'
        ),
        validators=[validate_username],
        error_messages={
            'unique': (
                'Пользователь с таким именем или'
                ' с таким емейлом уже существует'
            )
        }
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )
    role = models.CharField(
        verbose_name='Права пользователя',
        max_length=150,
        choices=USER_ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower',
            )
        ]

    def __str__(self):
        return self.user.username
