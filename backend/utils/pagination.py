from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    '''
    Кастомная пагинация с возможностью ограничения
    количества объектов при помощи значения limit в запросе.
    '''

    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50
