from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from decimal import Decimal, ROUND_HALF_UP


class SharedCart(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name='shared_carts')

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError("Cart name cannot be empty.")

    def total_shared_cost(self):
        return sum(i.quantity * (i.item.price or 0) for i in self.items.filter(is_shared=True))

    def total_personal_cost(self, user):
        return sum(i.quantity * (i.item.price or 0) for i in self.items.filter(is_shared=False, added_by=user))

    def total_cost(self):
        return sum(i.quantity * (i.item.price or 0) for i in self.items.all())

    def split_cost(self):
        total = self.total_shared_cost()
        num_users = self.users.count()
        return total / num_users if num_users else 0

from django.db import models

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

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    availability = models.BooleanField(default=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="N/A",
    )

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError("Item name cannot be empty.")
        if self.price is not None and self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.price = Decimal(self.price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.clean()  
        super().save(*args, **kwargs)

class CartItem(models.Model):
    cart = models.ForeignKey(SharedCart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_purchased = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in {self.cart.name}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(null=True, blank=True)  
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.message is None or self.message.strip() == "":
            raise ValidationError("Message cannot be empty.") 
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.message if self.message else "No Message"


class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_history')
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

class PaymentInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class UserActionHistory(models.Model):
    ACTION_TYPES = [
        ("ADD", "Add Item"),
        ("REMOVE", "Remove Item"),
        ("MODIFY", "Modify Item"),
        ("VIEW", "View Cart"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="action_history")
    cart = models.ForeignKey(SharedCart, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(GroceryItem, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp}"
