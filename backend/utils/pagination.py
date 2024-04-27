from django.conf import settings
from rest_framework import pagination


class PageLimitPagination(pagination.PageNumberPagination):
    '''
    Кастомная пагинация с возможностью ограничения
    количества объектов при помощи значения limit в запросе.
    '''

    page_size = settings.PAGINATION
    page_size_query_param = 'limit'
    max_page_size = 50
