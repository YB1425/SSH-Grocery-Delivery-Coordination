# main/admin.py
from django.contrib import admin
from .models import (
    SharedCart, GroceryItem, CartItem, Notification,
    PurchaseHistory, PaymentInfo
)

admin.site.register(SharedCart)
admin.site.register(GroceryItem)
admin.site.register(CartItem)
admin.site.register(Notification)
admin.site.register(PurchaseHistory)
admin.site.register(PaymentInfo)
