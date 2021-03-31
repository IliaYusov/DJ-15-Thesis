from django_filters.rest_framework import DjangoFilterBackend
from orders.filters import OrderFilter
from orders.models import Order
from orders.serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users.views import IsAdminOrOwner


class OrdersViewSet(ModelViewSet):

    queryset = Order.objects.all().prefetch_related('products').select_related('user')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            self.queryset = self.queryset.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['retrieve', 'list', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []
