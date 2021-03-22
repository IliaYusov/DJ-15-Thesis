from api_app.models import Product, ProductReview, Order, ProductCollection
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'price': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'name': ['iexact', 'icontains'],
            'description': ['icontains']
        }


class ProductReviewFilter(filters.FilterSet):
    class Meta:
        model = ProductReview
        fields = {
            'user': ['exact'],
            'product': ['exact'],
            'created_at': ['exact', 'date__gt', 'date__lt']
        }


class OrderFilter(filters.FilterSet):

    class Meta:
        model = Order
        fields = {
            'status': ['iexact'],
            'total_amount': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'created_at': ['exact', 'date__gt', 'date__lt'],
            'updated_at': ['exact', 'date__gt', 'date__lt'],
            'products__id': ['exact']
        }


class ProductCollectionFilter(filters.FilterSet):

    class Meta:
        model = ProductCollection
        fields = {
            'name': ['iexact', 'icontains'],
            'text': ['icontains'],
            'created_at': ['exact', 'date__gt', 'date__lt'],
            'updated_at': ['exact', 'date__gt', 'date__lt'],
            'products__id': ['exact']
        }
