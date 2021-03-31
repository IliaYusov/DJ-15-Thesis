from django.contrib import admin
from products.models import Product, ProductReview, ProductCollection


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at')
    list_display_links = ('id', 'name', 'price', 'created_at')
    list_filter = ('name', )
    search_fields = ('id', 'name')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'created_at')
    list_display_links = ('id', 'product', 'user', 'created_at')
    list_filter = ('user', 'created_at', ('product', admin.RelatedOnlyFieldListFilter))
    search_fields = ('id', 'product__name', 'user__username')


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'created_at')
    list_display_links = ('id', 'name', 'created_at')
    list_filter = ('name', )
    filter_horizontal = ('products', )
    search_fields = ('id', 'name')
