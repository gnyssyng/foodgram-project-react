from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User
from users.serializers import FollowReadSerializer, FollowSerializer


def response_400_user(message):
    '''Функция возвращающая код 400 и сообщение, передаваемое в функцию.'''
    return Response(message, status=status.HTTP_400_BAD_REQUEST)


class UserView(UserViewSet):
    '''
    Viewset для взаимодействия с моделью пользователя.

    Также, в нём описаны методы, которые управляют запросами к эндпоинтам
    /subsribe/ и /subsriptions/, связанным с моделью Follow,
    отвечающей за подписки пользователей.
    '''

    def get_queryset(self):
        return User.objects.all()

    def get_follow_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        '''Управляет GET-запросами к эндпоинту /users/me/'''
        instance = self.get_instance()
        if request.method == "GET" and self.request.user.is_authenticated:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                {
                    'invalid_credentials':
                    'Страница доступа только авторизованным пользователям.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, id):
        '''Управляет созданием и удалением подписок пользователя.'''
        following = get_object_or_404(User, id=int(id))
        serializer = FollowSerializer(
            data={'following': following.id, 'user': request.user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.get(
            following=following,
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def subscriptions(self, request):
        '''Возвращает список подписок пользователя.'''
        queryset = self.get_follow_queryset()
        pages = self.paginate_queryset(queryset)
        serializer = FollowReadSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
