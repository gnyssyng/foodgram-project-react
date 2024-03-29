from api.models import Tag, Ingredient, Recepie
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from api.serializers import TagSerializer


class TagViewSet(ReadOnlyModelViewSet):

    pagination_class = None
    permission_classes = [AllowAny,]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)
