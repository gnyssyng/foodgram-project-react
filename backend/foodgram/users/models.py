from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=254
    )
    username = models.CharField(
        'Уникальный юзернейм',
        unique=True,
        max_length=150
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=150
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписок на пользователя.'''

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        CustomUser,
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
