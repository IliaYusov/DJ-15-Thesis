from api_app.filters import ProductFilter, ProductReviewFilter, OrderFilter, ProductCollectionFilter
from api_app.serializers import ProductSerializer, ProductReviewSerializer, OrderSerializer, ProductCollectionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet
from api_app.models import Product, ProductReview, Order, ProductCollection


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAdminOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class ProductsViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [IsAdmin()]
        return []


class ProductReviewsViewSet(ModelViewSet):

    queryset = ProductReview.objects.all().select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductReviewFilter

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []


class OrdersViewSet(ModelViewSet):

    queryset = Order.objects.all().prefetch_related('products').select_related('user')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            self.queryset = self.queryset.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []


class ProductCollectionViewSet(ModelViewSet):

    queryset = ProductCollection.objects.all().prefetch_related('products')
    serializer_class = ProductCollectionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductCollectionFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return []
