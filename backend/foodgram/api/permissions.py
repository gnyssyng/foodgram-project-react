from rest_framework.permissions import BasePermission, AllowAny


class IsAuthorOrModeratorOrReadOnly(BasePermission):
    '''Право доступа для авторов объектов.'''

    def has_object_permission(self, request, view, obj):

        if request.path == 'users/me/' and request.user.is_authenticated:
            return True
        else:
            return AllowAny
