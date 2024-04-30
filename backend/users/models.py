from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_me, validate_pattern


class User(AbstractUser):
    '''Модель пользователя.'''

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=settings.EMAIL_LENGTH
    )
    username = models.CharField(
        'Уникальный юзернейм',
        unique=True,
        max_length=settings.USERS_CHAR_LENGTH,
        validators=[validate_pattern, validate_me]
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=settings.USERS_CHAR_LENGTH
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=settings.USERS_CHAR_LENGTH
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.USERS_CHAR_LENGTH
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписок на пользователя.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписка',
        related_name='following'
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['following', 'user'],
                name='unique_following'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        ]

        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подпсики'

    def __str__(self):
        return f'{self.user} {self.following}'
