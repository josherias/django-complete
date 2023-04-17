from dataclasses import fields
from decimal import Decimal
from pyexpat import model
from rest_framework import serializers
from .models import Cart, CartItem, Collection, Product, Review


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)
   

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'price', 'price_with_tax', 'collection']
   
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
   
    def calculate_tax(self, product: Product):
        return product.price * Decimal(1.1)
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
        
    # overide create method to access the product from url while create a new review
    def create(self, validated_data):
            product_id = self.context['product_id'];
            return Review.objects.create(product_id=product_id, **validated_data)
            

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.price
        
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
            
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True) #we only want to only read this field
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])
    
    class Meta:
        model = Cart
        # items is the related name on the cartitem model hence its a part of the cart as items
        fields = ['id', 'items', 'total_price'] 
        

    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    # validate specific field
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with given id was found.")
        return value
    
    
    # override default save method to prevent duplicate products in cart
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            # cart_item = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity)
            
        return self.instance
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
        

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']