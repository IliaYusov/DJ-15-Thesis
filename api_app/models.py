from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class OrderStatusChoices(models.TextChoices):
    """Статусы объявления."""
    NEW = "NEW", "Новый"
    IN_PROGRESS = "IN_PROGRESS", "В работе"
    DONE = "DONE", "Закрыт"


class Product(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'{self.id}, {self.name}'


class OrderPositions(models.Model):
    product = models.ForeignKey(Product,
                                related_name='orders',
                                on_delete=models.CASCADE)
    order = models.ForeignKey('Order',
                              related_name='positions',
                              on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, )
    text = models.TextField(blank=True, default='')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = ['user', 'product']


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through=OrderPositions)
    status = models.TextField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.NEW
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


class ProductCollection(models.Model):
    name = models.CharField(max_length=64)
    text = models.TextField(blank=True, default='')
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
