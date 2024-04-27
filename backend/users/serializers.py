from api.models import Recipe
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Follow, User
from utils.serializers import SimpleRecipeSerializer


def raise_validation_error(message):
    '''Вызывает ошибку валидации с переданным в функцию сообщением.'''
    raise ValidationError(message=message)


class UserCreateSerializer(UserCreateSerializer):
    '''
    Сериализатор для модели User.

    Предназначен для сериализации новых объектов модели.
    '''

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+$'
            ),
        ],
    )

    def validate(self, data):
        if data.get('username') == 'me':
            raise ValidationError(
                'Нельзя использоватя me в качестве юзернейма.'
            )
        return super().validate(data)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TokenCreateSerializer(serializers.Serializer):
    '''Сериалиазтор, предназначенный для создания токенов авторизации.'''

    default_error_messages = {
        'invalid_credentials': 'Ввендены неккоректные данные.'
    }

    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['email'] = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get('password')
        params = {'email': attrs.get('email')}
        self.user = authenticate(
            request=self.context.get('request'), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail('invalid_credentials')
        if self.user and self.user.is_active:
            return attrs
        self.fail('invalid_credentials')


class UserSerializer(UserSerializer):
    '''
    Сериализатор модели CustomUSer.

    Предназначен для десереализации объектов модели.
    '''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user:
            raise ValidationError(
                'Неавторизированный пользователь.'
            )
        return request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            following=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания объектов модели Follow.'''

    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['following', 'user']

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            if Follow.objects.filter(
                user=data.get('user'), following=data.get('following')
            ).exists():
                raise_validation_error('Подписка уже существует')
            if data.get('user') == data.get('following'):
                raise_validation_error('Нельзя подписаться на самого себя.')
            return super().validate(data)
        try:
            Follow.objects.get(
                following=data.get('following'),
                user=data.get('user')
            )
        except Follow.DoesNotExist:
            raise_validation_error('Несуществующая подписка.')
        return super().validate(data)

    def to_representation(self, instance):
        try:
            recipe_limit = int(
                self.context.get('request').GET.get('recipes_limit')
            )
        except Exception:
            recipe_limit = None
        data = super().to_representation(instance)
        following_user = User.objects.get(id=data['following'])
        following_user_recipes = Recipe.objects.filter(
            author=following_user
        )[:recipe_limit]
        return {
            'email': following_user.email,
            'id': following_user.pk,
            'username': following_user.username,
            'first_name': following_user.first_name,
            'last_name': following_user.last_name,
            'is_subscribed': Follow.objects.filter(
                user=following_user,
                following=data['user']
            ).exists(),
            'recipes': SimpleRecipeSerializer(
                following_user_recipes,
                many=True,
                context={'request': self.context.get('request')}
            ).data,
            'recipes_count': len(following_user_recipes)
        }


class FollowReadSerializer(serializers.ModelSerializer):
    '''Сериализатор для чтения объектов модели Follow.'''

    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ['following', 'user']

    def to_representation(self, instance):
        try:
            recipe_limit = int(
                self.context.get('request').GET.get('recipes_limit')
            )
        except Exception:
            recipe_limit = None
        data = super().to_representation(instance)
        following_user = User.objects.get(id=data['following'])
        following_user_recipes = Recipe.objects.filter(
            author=following_user
        )[:recipe_limit]
        return {
            'email': following_user.email,
            'id': following_user.pk,
            'username': following_user.username,
            'first_name': following_user.first_name,
            'last_name': following_user.last_name,
            'is_subscribed': Follow.objects.filter(
                user=following_user,
                following=data['user']
            ).exists(),
            'recipes': SimpleRecipeSerializer(
                following_user_recipes,
                many=True,
                context={'request': self.context.get('request')}
            ).data,
            'recipes_count': len(following_user_recipes)
        }
