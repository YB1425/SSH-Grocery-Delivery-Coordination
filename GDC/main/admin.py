# main/admin.py
from django.contrib import admin
from .models import *


@admin.register(UserActionHistory)
class UserActionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'item', 'cart', 'quantity', 'timestamp', 'details')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('user__username', 'item__name', 'cart__name', 'details')

admin.site.register(SharedCart)
admin.site.register(GroceryItem)
admin.site.register(CartItem)
admin.site.register(Notification)
admin.site.register(PurchaseHistory)
admin.site.register(PaymentInfo)
