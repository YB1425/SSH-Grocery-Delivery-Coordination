from decimal import Decimal
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from .models import SharedCart, GroceryItem, CartItem, Notification
from django.core.exceptions import ValidationError


class SharedCartTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        self.cart = SharedCart.objects.create(name='Flat A Cart')
        self.cart.users.add(self.user1, self.user2)
        self.item1 = GroceryItem.objects.create(name='Apples', price=Decimal('1.50'), availability=True)
        self.item2 = GroceryItem.objects.create(name='Milk', price=Decimal('0.99'), availability=True)
        CartItem.objects.create(cart=self.cart, item=self.item1, quantity=3, added_by=self.user1)
        CartItem.objects.create(cart=self.cart, item=self.item2, quantity=2, added_by=self.user2)

    def test_total_cost(self):
        self.assertEqual(
            self.cart.total_cost(),
            Decimal('3') * Decimal('1.50') + Decimal('2') * Decimal('0.99')
        )

    def test_split_cost(self):
        self.assertAlmostEqual(
            self.cart.split_cost(),
            (Decimal('3') * Decimal('1.50') + Decimal('2') * Decimal('0.99')) / Decimal('2')
        )

    def test_empty_cart(self):
        empty_cart = SharedCart.objects.create(name='Empty Cart')
        self.assertEqual(empty_cart.total_cost(), Decimal('0'))
        self.assertEqual(empty_cart.split_cost(), Decimal('0'))

    def test_no_users(self):
        self.cart.users.clear()
        self.assertEqual(self.cart.split_cost(), Decimal('0'))

    def test_concurrent_updates(self):
        self.cart.users.add(User.objects.create_user(username='user3', password='test123'))
        CartItem.objects.create(cart=self.cart, item=self.item1, quantity=1, added_by=self.user1)
        self.assertEqual(
            self.cart.total_cost(),
            Decimal('4') * Decimal('1.50') + Decimal('2') * Decimal('0.99')
        )

class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='test123')
        self.notification = Notification.objects.create(user=self.user, message="Test notification")

    def test_notification_creation(self):
        self.assertEqual(self.notification.user, self.user)
        self.assertFalse(self.notification.is_read)

    def test_mark_as_read(self):
        self.notification.is_read = True
        self.notification.save()
        self.assertTrue(self.notification.is_read)

    def test_item_addition_notification(self):
        cart = SharedCart.objects.create(name="Test Cart")
        cart.users.add(self.user)
        item = GroceryItem.objects.create(name="Bread", price=Decimal('2.0'), availability=True)
        CartItem.objects.create(cart=cart, item=item, quantity=1, added_by=self.user)
        notification = Notification.objects.create(user=self.user, message=f"Added {item.name} to {cart.name}")
        self.assertIn("Added Bread to Test Cart", notification.message)

class GroceryItemTests(TestCase):
    def test_valid_grocery_item(self):
        item = GroceryItem.objects.create(name="Bananas", price=Decimal('0.50'), availability=True)
        self.assertEqual(item.name, "Bananas")
        self.assertEqual(item.price, Decimal('0.50'))
        self.assertTrue(item.availability)

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            GroceryItem(name="Invalid Item", price=Decimal('-1')).save()

    def test_missing_required_fields(self):
        item = GroceryItem(price=Decimal('1.0'), availability=True)
        with self.assertRaises(ValidationError):
         item.full_clean()
         item.save()

    def test_category_choices(self):
        item = GroceryItem.objects.create(name="Orange Juice", category="Beverages")
        self.assertEqual(item.category, "Beverages")

class CartItemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='test123')
        self.cart = SharedCart.objects.create(name="User Cart")
        self.cart.users.add(self.user)
        self.item = GroceryItem.objects.create(name="Bread", price=Decimal('2.0'), availability=True)

    def test_add_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        self.assertEqual(cart_item.quantity, 2)
        self.assertFalse(cart_item.is_purchased)

    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        cart_item.quantity = 5
        cart_item.save()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=2, added_by=self.user)
        cart_item.delete()
        self.assertEqual(self.cart.items.count(), 0)

    def test_purchase_cart_item(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.item, quantity=1, added_by=self.user)
        cart_item.is_purchased = True
        cart_item.save()
        self.assertTrue(cart_item.is_purchased)

class SimulatedAPITests(TestCase):
    def test_item_price_update(self):
        from .views import update_item_price_and_availability
        price, availability = update_item_price_and_availability("Apples")
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        self.assertIsInstance(availability, bool)
