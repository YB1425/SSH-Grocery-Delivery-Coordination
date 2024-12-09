from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from main.models import SharedCart, GroceryItem, CartItem


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

    def test_remove_user(self):
        self.cart.users.remove(self.user1)
        self.assertNotIn(self.user1, self.cart.users.all())

    def test_cart_str_representation(self):
        self.assertEqual(str(self.cart), 'Flat A Cart')

    def test_cart_with_duplicate_users(self):
        initial_user_count = self.cart.users.count()
        self.cart.users.add(self.user1)  
        self.assertEqual(self.cart.users.count(), initial_user_count)
