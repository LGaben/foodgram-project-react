from rest_framework.pagination import PageNumberPagination


class CastomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
