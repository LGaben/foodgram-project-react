from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet


class ListViewSet(
    ListModelMixin,
    GenericViewSet
):
    pass
