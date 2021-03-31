from django_filters import rest_framework as filters
from products.models import Product, ProductReview, ProductCollection


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'lte', 'gte'],
            'name': ['iexact', 'icontains'],
            'description': ['icontains']
        }


class ProductReviewFilter(filters.FilterSet):
    class Meta:
        model = ProductReview
        fields = {
            'user': ['exact'],
            'product': ['exact'],
            'created_at': ['date', 'date__gte', 'date__lte']
        }


class ProductCollectionFilter(filters.FilterSet):

    class Meta:
        model = ProductCollection
        fields = {
            'name': ['iexact', 'icontains']
        }
