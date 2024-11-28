# main/models.py
from django.db import models
from django.contrib.auth.models import User

class SharedCart(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name='shared_carts')

    def __str__(self):
        return self.name

    def total_cost(self):
        total = sum(
            item.quantity * (item.item.price or 0) for item in self.items.all()
        )
        return total

    def split_cost(self):
        total = self.total_cost()
        num_users = self.users.count()
        return total / num_users if num_users else 0

class GroceryItem(models.Model):
    CATEGORY_CHOICES = [
        ("Fruits", "Fruits"),
        ("Vegetables", "Vegetables"),
        ("Dairy", "Dairy"),
        ("Bakery", "Bakery"),
        ("Meat", "Meat"),
        ("Beverages", "Beverages"),
        ("Snacks", "Snacks"),
        ("Frozen Foods", "Frozen Foods"),
        ("Household Items", "Household Items"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    availability = models.BooleanField(default=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="N/A",  # Default category
    )

    def __str__(self):
        return self.name

    
class CartItem(models.Model):
    cart = models.ForeignKey(SharedCart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in {self.cart.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_history')
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

class PaymentInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add secure fields for payment information
