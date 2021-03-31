from django_filters.rest_framework import DjangoFilterBackend
from products.filters import ProductFilter, ProductReviewFilter, ProductCollectionFilter
from products.models import Product, ProductReview, ProductCollection
from products.serializers import ProductSerializer, ProductReviewSerializer, ProductCollectionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users.views import IsAdminOrOwner, IsAdmin


class ProductsViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [IsAdmin()]
        return []


class ProductReviewsViewSet(ModelViewSet):

    queryset = ProductReview.objects.all().select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductReviewFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminOrOwner()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []


class ProductCollectionViewSet(ModelViewSet):

    queryset = ProductCollection.objects.all().prefetch_related('products')
    serializer_class = ProductCollectionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductCollectionFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return []