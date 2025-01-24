from rest_framework import serializers
from .models import Product, Order, OrderItem


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
        if value == '':  # Handle empty string
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

    