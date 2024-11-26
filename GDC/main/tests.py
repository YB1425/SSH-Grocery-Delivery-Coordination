# main/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import SharedCart, GroceryItem, CartItem

class SharedCartTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.cart = SharedCart.objects.create(name='Test Cart')
        self.cart.users.add(self.user1, self.user2)
        self.item = GroceryItem.objects.create(name='Milk', price=1.50)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, item=self.item, quantity=2, added_by=self.user1
        )

    def test_cart_total_cost(self):
        total_cost = self.cart.total_cost()
        self.assertEqual(total_cost, 3.00)

    def test_split_cost(self):
        split_cost = self.cart.split_cost()
        self.assertEqual(split_cost, 1.50)

    def test_add_cart_item(self):
        item2 = GroceryItem.objects.create(name='Bread', price=2.00)
        CartItem.objects.create(
            cart=self.cart, item=item2, quantity=1, added_by=self.user2
        )
        self.assertEqual(self.cart.items.count(), 2)

    def test_remove_cart_item(self):
        self.cart_item.delete()
        self.assertEqual(self.cart.items.count(), 0)
