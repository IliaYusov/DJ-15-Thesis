from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class OrderStatusChoices(models.TextChoices):
    """Статусы заказов."""
    NEW = "NEW", "Новый"
    IN_PROGRESS = "IN_PROGRESS", "В работе"
    DONE = "DONE", "Закрыт"


class Product(models.Model):
    """Модель Товары"""
    name = models.CharField(
        max_length=128,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Цена'
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
        return f'ID_{self.id} - {self.name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


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


class ProductReview(models.Model):
    """Модель Отзывы на товары"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст отзыва')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
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
        return f'ID_{self.id} - ({self.product}), {self.user}'

    class Meta:
        unique_together = ['user', 'product']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


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


class ProductCollection(models.Model):
    """Модель Подборки товаров"""
    name = models.CharField(
        max_length=64,
        verbose_name='Название'
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст'
    )
    products = models.ManyToManyField(
        Product,
        verbose_name='Продукты'
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
        return f'ID_{self.id} - {self.name}'

    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'
