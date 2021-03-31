from django_filters import rest_framework as filters
from orders.models import Order


class OrderFilter(filters.FilterSet):

    class Meta:
        model = Order
        fields = {
            'status': ['iexact'],
            'total_amount': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'created_at': ['date', 'date__gte', 'date__lte'],
            'updated_at': ['date', 'date__gte', 'date__lte'],
            'products__id': ['exact']
        }
