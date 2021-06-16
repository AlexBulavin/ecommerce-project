from django.contrib import admin
from .models import Category, Product, Cart, CartItem  #, DeliveryType, OrderStatus
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
# admin.site.register(DeliveryType)
admin.site.register(CartItem)
# admin.site.register(OrderStatus)
