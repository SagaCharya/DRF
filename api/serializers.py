from rest_framework import serializers
from .models import Product, Order, OrderItem, User
from django.db import transaction


class UserSerilizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'is_staff',
            'is_superuser',
            'is_authenticated',
            'orders'
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
            'description',
            'stock',
            'price',
        )
    
    def validate_stock(self, value):
        if value is None or value == '':  # Handle empty string
            return 0
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Stock must be a non-negative integer.")
        return value


    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0"
            )
        return value
    
class OrderItemSerilizer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', decimal_places=2, max_digits=10, allow_null = True)
    class Meta:
        model = OrderItem
        fields= (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
        )


class OrderCreateSerilizer(serializers.ModelSerializer):
    class OrderItemCreateSerilizer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerilizer(many = True, required= False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')

        with transaction.atomic():
            instance = super().update(instance, validated_data)
    
            if orderitem_data is not None:
                instance.items.all().delete()
    
                for item in orderitem_data:
                    OrderItem.objects.create(order= instance, **item)

        return instance


    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in orderitem_data:
                OrderItem.objects.create(order= order, **item)


        return order

    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items',
        )

        extra_kwargs = {
            'user': {
                "read_only" : True
            }
        }
    
class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only = True)
    items = OrderItemSerilizer(many = True, read_only = True)
    total_prize = serializers.SerializerMethodField(method_name='total')

    def total(self,obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields=(
            'order_id',
            'created_at',
            'user',
            'status',
            'items',
            'total_prize'
        )


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many = True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()

    