from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import CustomUser, Follow


class CustomUserCreateSerializer(UserCreateSerializer):
    '''
    Сериализатор для модели CustomUser,
    предназначенный для создания новых объектов модели.
    '''

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all())
        ]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+$'
            ),
        ],
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomTokenCreateSerializer(serializers.Serializer):
    '''
    Сериалиазтор, предназначенный для создания токенов авторизации.
    '''

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
            self.user = CustomUser.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail('invalid_credentials')
        if self.user and self.user.is_active:
            return attrs
        self.fail('invalid_credentials')


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор модели CustomUSer,
    предназначенный для чтения объектов модели.
    '''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
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
        if request.user.is_authenticated:
            user = request.user
            subscribed = Follow.objects.filter(
                user=user,
                following=obj
            ).exists()
            return subscribed
        return False
