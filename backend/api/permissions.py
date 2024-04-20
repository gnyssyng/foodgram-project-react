from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    '''Право доступа для авторов объектов.'''

    def has_object_permission(self, request, view, obj):
        return obj.author.id == request.user.id
