from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''Модель пользователя.'''

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=settings.MAX_CHAR_LENGTH,
        ubique=True,
        verbose_name='Логин'
    )
    first_name = models.CharField(
        max_length=settings.MAX_CHAR_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.MAX_CHAR_LENGTH,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=settings.MAX_CHAR_LENGTH,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['first_name']


class Follow(models.Model):
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
