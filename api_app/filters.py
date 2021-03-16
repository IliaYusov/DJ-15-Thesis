from api_app.models import Product
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):

    price = filters.NumberFilter()
    name = filters.CharFilter()
    description = filters.CharFilter()

    class Meta:
        model = Product
        fields = ['price', 'name', 'description']
