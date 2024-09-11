from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import serializers
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price'] 

   
class OrderSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', ' title', 'price']

class CartSerializer(serializers.ModelSerializer):
    menuitem = CartItemSerializer
    class Meta():
        model = Cart
        fields = ['menuitem', 'quantity', 'price']


class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields= ['menuitem', 'quantity', 'unit_price']

class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']


class SingleOrderMenuSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title','price']


class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleOrderMenuSerializer()
    class Meta():
        model = OrderItem
        fields = ['menuitem','quantity']


class OrderInsertSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']