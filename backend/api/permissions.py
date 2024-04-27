from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    '''Право доступа для авторов объектов.'''

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return obj.author == request.user
