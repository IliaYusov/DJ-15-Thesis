from rest_framework import serializers
from api_app.models import Product, ProductReview, Order, OrderPositions, ProductCollection
from django.contrib.auth.models import User
from rest_framework.fields import DecimalField


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0,
        max_value=999999,
    )

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)


class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(
        read_only=True,
    )

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'product', 'text', 'rating', 'created_at', 'updated_at')

    def validate(self, data):

        if 'product_id' not in self.context['request'].data:  # Проверяем product_id
            raise serializers.ValidationError('product_id: This field is required.')
        product_id = self.context['request'].data['product_id']
        if not isinstance(product_id, int):
            raise serializers.ValidationError('product_id should be integer')
        if not Product.objects.filter(id=product_id):
            raise serializers.ValidationError('Wrong product_id')

        user_id = self.context['request'].user.id  # Проверяем что отзыв на один продукт только один
        if ProductReview.objects.filter(user=user_id).filter(id=product_id):
            raise serializers.ValidationError('Maximum one review per user per product')
        return data

    def create(self, validated_data):
        """ Простановка значения поля user по-умолчанию и product по product.id"""
        validated_data['user'] = self.context['request'].user
        validated_data['product'] = Product.objects.get(id=self.context['request'].data['product_id'])
        return super().create(validated_data)


class OrderPositionsSerializer(serializers.Serializer):

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderSerializer(serializers.ModelSerializer):

    products = OrderPositionsSerializer(
        many=True,
        source="positions",
    )

    user = UserSerializer(
        read_only=True,
    )

    total_amount = DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'products', 'status', 'total_amount', 'created_at', 'updated_at')

    def create(self, validated_data):

        validated_data['user'] = self.context['request'].user  # Проставляем значения поля user по-умолчанию
        positions_data = validated_data.pop('positions')

        total_amount = 0  # Считаем и добавляем в validated_data total_amount
        if positions_data:
            for position in positions_data:
                total_amount += position['product_id'].price * position['quantity']
        validated_data['total_amount'] = total_amount

        order = super().create(validated_data)

        if positions_data:  # Создаем поля в промежуточной таблице
            to_save = []
            for position in positions_data:
                to_save.append(OrderPositions(
                    product=position['product_id'],
                    quantity=position['quantity'],
                    order_id=order.id,
                ))
            OrderPositions.objects.bulk_create(to_save)

        return order

    def validate(self, data):
        """Проверяем, что статус могут менять только админы"""
        if not self.context['request'].user.is_staff and 'status' in data:
            raise serializers.ValidationError('Status is read-only for users')
        product_ids = set()
        for position in data['positions']:
            product_ids.add(position['product_id'])
        if len(product_ids) != len(data['positions']):
            raise serializers.ValidationError('Products should be unique')
        return data


class ProductCollectionSerializer(serializers.ModelSerializer):

    products = ProductSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ProductCollection
        fields = ('id', 'name', 'text', 'products', 'created_at', 'updated_at')

    def create(self, validated_data):
        product_ids_list = []
        for product in self.context['request'].data['products']:
            product_ids_list.append(product['product_id'])
        validated_data['products'] = Product.objects.filter(id__in=product_ids_list)
        return super().create(validated_data)

    def validate(self, data):
        if 'products' not in self.context['request'].data:
            raise serializers.ValidationError('products: This field is required.')
        products_list = self.context['request'].data['products']
        if not isinstance(products_list, list):
            raise serializers.ValidationError('products should be list')
        product_ids = []
        for product in products_list:
            if isinstance(product, dict):
                product_ids.append(product.get('product_id'))
        if len(set(product_ids)) != len(product_ids):
            raise serializers.ValidationError('products should be unique')
        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise serializers.ValidationError('wrong product_id')
        return data
