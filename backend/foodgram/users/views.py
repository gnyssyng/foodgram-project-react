from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Follow
from rest_framework.permissions import IsAuthenticated


class UserMeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_sub = Follow.objects.filter(
            user=user,
        ).exists()

        return Response(
            {
                'email': user.email,
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_subscribed': is_sub
            }
        )
