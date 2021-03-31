from django.conf import settings
from django.db import models
from products.models import Product


class OrderStatusChoices(models.TextChoices):
    """Статусы заказов."""
    NEW = "NEW", "Новый"
    IN_PROGRESS = "IN_PROGRESS", "В работе"
    DONE = "DONE", "Закрыт"


class OrderPositions(models.Model):
    """Промежуточная модель Позиций в заказе"""
    product = models.ForeignKey(
        Product,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    order = models.ForeignKey(
        'Order',
        related_name='positions',
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'


class Order(models.Model):
    """Модель Заказы"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    products = models.ManyToManyField(
        Product,
        through=OrderPositions,
        verbose_name='Позиции'
    )
    status = models.TextField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.NEW,
        verbose_name='Статус заказа'
    )
    total_amount = models.DecimalField(
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name='Общая сумма'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f'ID_{self.id} - {self.user}, {self.status}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
