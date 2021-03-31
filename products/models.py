from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


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
        return f'{self.name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


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
