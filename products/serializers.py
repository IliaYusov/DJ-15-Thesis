from products.models import Product, ProductReview, ProductCollection
from rest_framework import serializers
from users.serializers import UserSerializer


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
        if ProductReview.objects.filter(user=user_id).filter(product=product_id):
            if self.context['request'].stream.method == 'POST':
                raise serializers.ValidationError('Maximum one review per user per product')
            elif self.context['request'].stream.method in ['PUT', 'PATCH']:
                if product_id != self.instance.product_id:
                    raise serializers.ValidationError("You already reviewed this product")
        return data

    def create(self, validated_data):
        """ Простановка значения поля user по-умолчанию и product по product.id"""
        validated_data['user'] = self.context['request'].user
        validated_data['product'] = Product.objects.get(id=self.context['request'].data['product_id'])
        return super().create(validated_data)


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
