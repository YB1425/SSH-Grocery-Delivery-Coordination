from django.forms import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Notification, SharedCart, GroceryItem, CartItem
from decimal import Decimal


class NotificationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')
        self.cart = SharedCart.objects.create(name="Test Cart")
        self.notification1 = Notification.objects.create(user=self.user1, message="Notification 1")
        self.notification2 = Notification.objects.create(user=self.user1, message="Notification 2")
        self.notification3 = Notification.objects.create(user=self.user2, message="Notification 3")

    def test_notification_creation(self):
        self.assertEqual(self.notification1.user, self.user1)
        self.assertFalse(self.notification1.is_read)

    def test_mark_notification_as_read(self):
        self.notification1.is_read = True
        self.notification1.save()
        self.assertTrue(self.notification1.is_read)

    def test_mark_notification_as_unread(self):
        self.notification1.is_read = True
        self.notification1.save()
        self.notification1.is_read = False
        self.notification1.save()
        self.assertFalse(self.notification1.is_read)

    def test_multiple_notifications_for_user(self):
        notifications = Notification.objects.filter(user=self.user1)
        self.assertEqual(notifications.count(), 2)

    def test_notifications_for_different_users(self):
        user1_notifications = Notification.objects.filter(user=self.user1)
        user2_notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(user1_notifications.count(), 2)
        self.assertEqual(user2_notifications.count(), 1)

    def test_delete_notification(self):
        self.notification1.delete()
        notifications = Notification.objects.filter(user=self.user1)
        self.assertEqual(notifications.count(), 1)

    def test_clear_all_notifications_for_user(self):
        Notification.objects.filter(user=self.user1).delete()
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)

    def test_item_added_notification(self):
        self.cart.users.add(self.user1)
        item = GroceryItem.objects.create(name="Bread", price=Decimal('2.0'), availability=True)
        CartItem.objects.create(cart=self.cart, item=item, quantity=1, added_by=self.user1)
        notification = Notification.objects.create(user=self.user1, message=f"Added {item.name} to {self.cart.name}")
        self.assertIn("Added Bread to Test Cart", notification.message)

    def test_notification_without_message(self):
        with self.assertRaises(ValidationError):
            Notification.objects.create(user=self.user1, message=None)



    def test_notification_str_representation(self):
        self.assertEqual(str(self.notification1), "Notification 1")

    def test_mark_all_notifications_as_read(self):
        Notification.objects.filter(user=self.user1).update(is_read=True)
        notifications = Notification.objects.filter(user=self.user1, is_read=True)
        self.assertEqual(notifications.count(), 2)

    def test_mark_all_notifications_as_unread(self):
        Notification.objects.filter(user=self.user1).update(is_read=False)
        notifications = Notification.objects.filter(user=self.user1, is_read=False)
        self.assertEqual(notifications.count(), 2)

    def test_notification_for_cart_removal(self):
        self.cart.users.add(self.user1)
        self.cart.users.remove(self.user1)
        notification = Notification.objects.create(user=self.user1, message=f"You were removed from {self.cart.name}")
        self.assertIn("You were removed from Test Cart", notification.message)

    def test_notification_for_cart_deletion(self):
        self.cart.delete()
        notification = Notification.objects.create(user=self.user1, message=f"Cart {self.cart.name} was deleted")
        self.assertIn("Cart Test Cart was deleted", notification.message)

    def test_create_bulk_notifications(self):
        notifications = [
            Notification(user=self.user1, message=f"Notification {i}") for i in range(1, 6)
        ]
        Notification.objects.bulk_create(notifications)
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 7)
