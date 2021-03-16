from api_app.filters import ProductFilter
from api_app.serializers import ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet
from api_app.models import Product


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff


class ProductsViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [IsAdmin()]
        return []
