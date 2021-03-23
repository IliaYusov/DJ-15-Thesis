from django.contrib import admin
from api_app.models import ProductCollection, Product, Order, ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at')
    list_display_links = ('id', 'name', 'price', 'created_at')
    list_filter = ('name', )


class PositionsInline(admin.TabularInline):
    model = Order.products.through


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'created_at')
    list_display_links = ('id', 'product', 'user', 'created_at')
    list_filter = ('user', 'created_at', ('product', admin.RelatedOnlyFieldListFilter))


def product_quantity(obj):
    return len(obj.products.all())


product_quantity.short_description = 'Кол-во товаров'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', product_quantity, 'status', 'created_at')
    list_display_links = ('id', 'user', product_quantity, 'status', 'created_at')
    list_filter = ('user', 'created_at')
    ordering = ('-created_at', )
    inlines = [PositionsInline]


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'created_at')
    list_display_links = ('id', 'name', 'created_at')
    list_filter = ('name', )
    filter_horizontal = ('products', )
