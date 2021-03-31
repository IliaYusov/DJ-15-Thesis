from django.contrib import admin
from orders.models import Order


class PositionsInline(admin.TabularInline):
    model = Order.products.through
    extra = 0


def product_quantity(obj):
    return len(obj.products.all())


product_quantity.short_description = 'Кол-во товаров'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', product_quantity, 'status', 'created_at')
    list_display_links = ('id', 'user', product_quantity, 'status', 'created_at')
    list_filter = ('user', 'created_at', 'status')
    ordering = ('-created_at', )
    inlines = [PositionsInline]
    search_fields = ('id', 'user__username', 'products__name')
    readonly_fields = ('total_amount', )
