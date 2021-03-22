from django.contrib import admin
from api_app.models import ProductCollection, Product, Order, ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    pass
