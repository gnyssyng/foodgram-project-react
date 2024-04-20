from api.models import Recipe
from api.serializers import FollowSerializer
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser, Follow


def response_400_user(message):
    '''Функция возвращающая код 400 и сообщение, передаваемое в функцию.'''
    return Response(message, status=status.HTTP_400_BAD_REQUEST)


class CustomUserView(UserViewSet):
    '''
    Viewset для взаимодействия с моделью пользователя.
    Также, в нём описаны методы, которые управляют запросами к эндпоинтам
    /subsribe/ и /subsriptions/, связанным с моделью Follow,
    отвечающей за подписки пользователей.
    '''

    ERRORS = {
        'double_subscription':
        {'errors': 'Невозможно подписаться дважды'},
        'self_subscription':
        {'erorrs': 'Невозможно подписаться на самого себя.'},
        'user_not_found':
        {'detail': 'Пользователя нет в подписках.'},
        'not_authenticated':
        {'detail': 'Учетные данные не были предоставлены.'}
    }

    def get_follow_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        if 'limit' in self.request.GET:
            limit = int(self.request.GET.get('limit'))
            queryset = queryset[:limit]
        return queryset

    def get_paginated_serializer_data(self, queryset):

        if 'recipes_limit' in self.request.GET:
            recipes_limit = int(self.request.GET.get('recipes_limit'))
        else:
            recipes_limit = None
        recipes = Recipe.objects.filter(
            author_id__in=self.get_follow_queryset().values_list(
               'following', flat=True
            )
        ).order_by('id')
        print(recipes)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={
                'request': self.request,
                'recipes': recipes,
                'recipes_limit': recipes_limit
            }
        )
        return serializer

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        '''Управляет GET-запросами к эндпоинту /users/me/'''
        instance = self.get_instance()
        if request.method == "GET" and self.request.user.is_authenticated:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                    self.ERRORS.get('not_authenticated'),
                    status=status.HTTP_401_UNAUTHORIZED
                )

    @action(
            ['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated, ]
        )
    def subscribe(self, request, id):
        '''Управляет созданием и удалением подписок пользователя.'''
        following = get_object_or_404(CustomUser, id=int(id))
        if request.method == 'POST':
            if not request.user == following:
                try:
                    Follow.objects.create(
                        user=request.user,
                        following=following
                    )
                except IntegrityError:
                    return response_400_user(
                        self.ERRORS.get('double_subscription')
                    )
                return Response(
                    self.get_paginated_serializer_data(
                        self.get_follow_queryset()
                    ).data[0],
                    status=status.HTTP_201_CREATED
                )
            else:
                return response_400_user(self.ERRORS.get('self_subscription'))
        elif request.method == 'DELETE':
            try:
                follow = Follow.objects.get(
                    user=request.user,
                    following=following
                )
                follow.delete()
            except Follow.DoesNotExist:
                return response_400_user(self.ERRORS.get('user_not_found'))
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def subscriptions(self, request):
        '''Возвращает список подписок пользователя.'''
        if request.method == 'GET':
            queryset = self.get_follow_queryset()
            data = self.get_paginated_serializer_data(queryset).data
            return self.get_paginated_response(data)
