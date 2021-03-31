from orders.models import Order, OrderPositions
from products.models import Product
from rest_framework import serializers
from rest_framework.fields import DecimalField
from users.serializers import UserSerializer


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

    def update(self, instance, validated_data):
        validated_data['user'] = instance.user  # Проставляем значения поля user из оригинального заказа

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
        if 'positions' in data:
            product_ids = set()
            for position in data['positions']:
                product_ids.add(position['product_id'])
            if len(product_ids) != len(data['positions']):
                raise serializers.ValidationError('Products should be unique')
        return data
