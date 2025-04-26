from rest_framework import serializers
from .models import User, Vendor, Product, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Vendor
        fields = ['id', 'user', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'vendor', 'name', 'description', 'price', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'created_at', 'total', 'status', 'items']