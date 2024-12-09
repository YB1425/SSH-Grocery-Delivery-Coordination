from django.test import TestCase
from django.contrib.auth.models import User
from main.models import SharedCart, GroceryItem, CartItem
from decimal import Decimal


class CartItemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='test123')
        self.cart = SharedCart.objects.create(name="Test Cart")
        self.cart.users.add(self.user)
        self.item = GroceryItem.objects.create(name="Bread", price=Decimal('2.0'), availability=True)

    def test_add_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        cart_item.quantity = 5
        cart_item.save()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        cart_item.delete()
        self.assertEqual(self.cart.items.count(), 0)

    def test_cart_item_string_representation(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        self.assertEqual(str(cart_item), "2 x Bread in Test Cart")

    def test_purchase_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        cart_item.is_purchased = True
        cart_item.save()
        self.assertTrue(cart_item.is_purchased)

    def test_cart_item_with_invalid_quantity(self):
        with self.assertRaises(Exception):
            CartItem.objects.create(cart=self.cart, item=self.item, quantity=-1, added_by=self.user)

    def test_cart_item_auto_added_at(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        self.assertIsNotNone(cart_item.added_at)

    def test_cart_item_associated_with_cart(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        self.assertEqual(cart_item.cart, self.cart)

    def test_cart_item_is_shared_default(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        self.assertTrue(cart_item.is_shared)

    def test_cart_item_can_be_unshared(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        cart_item.is_shared = False
        cart_item.save()
        self.assertFalse(cart_item.is_shared)

    def test_cart_item_is_purchased_default(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        self.assertFalse(cart_item.is_purchased)

    def test_cart_item_with_no_user(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=None)
        self.assertIsNone(cart_item.added_by)

    def test_cart_item_associated_with_grocery_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        self.assertEqual(cart_item.item, self.item)

    def test_multiple_cart_items_in_cart(self):
        item2 = GroceryItem.objects.create(name="Milk", price=Decimal('1.5'), availability=True)
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        CartItem.objects.create(cart=self.cart, item=item2, quantity=2, added_by=self.user)
        self.assertEqual(self.cart.items.count(), 2)

    def test_cart_item_price_total(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=3, added_by=self.user)
        self.assertEqual(cart_item.quantity * self.item.price, Decimal('6.0'))
