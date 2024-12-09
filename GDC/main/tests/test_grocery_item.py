from django.test import TestCase
from main.models import GroceryItem
from decimal import Decimal
from django.core.exceptions import ValidationError


class GroceryItemTests(TestCase):
    def test_create_valid_grocery_item(self):
        item = GroceryItem.objects.create(name="Apples", price=Decimal('1.50'), availability=True)
        self.assertEqual(item.name, "Apples")

    def test_grocery_item_without_price(self):
        item = GroceryItem.objects.create(name="Bananas", availability=True)
        self.assertIsNone(item.price)

    def test_grocery_item_string_representation(self):
        item = GroceryItem.objects.create(name="Oranges")
        self.assertEqual(str(item), "Oranges")

    def test_grocery_item_invalid_price(self):
        with self.assertRaises(Exception):
            GroceryItem.objects.create(name="Invalid Item", price=Decimal('-1'))

    def test_default_category(self):
        item = GroceryItem.objects.create(name="Carrots")
        self.assertEqual(item.category, "N/A")

    def test_set_valid_category(self):
        item = GroceryItem.objects.create(name="Milk", category="Dairy")
        self.assertEqual(item.category, "Dairy")

    def test_unavailable_grocery_item(self):
        item = GroceryItem.objects.create(name="Eggs", price=Decimal('2.0'), availability=False)
        self.assertFalse(item.availability)

    def test_grocery_item_description_blank(self):
        item = GroceryItem.objects.create(name="Watermelon", price=Decimal('3.50'))
        self.assertEqual(item.description, "")

    def test_price_update(self):
        item = GroceryItem.objects.create(name="Cheese", price=Decimal('4.0'))
        item.price = Decimal('4.5')
        item.save()
        self.assertEqual(item.price, Decimal('4.5'))

    def test_category_choices(self):
        item = GroceryItem.objects.create(name="Juice", category="Beverages")
        self.assertEqual(item.category, "Beverages")

    def test_invalid_category_choice(self):
        item = GroceryItem(name="Unknown", category="Invalid")
        with self.assertRaises(ValidationError):
            item.full_clean()  

    def test_duplicate_items(self):
        GroceryItem.objects.create(name="Potatoes", price=Decimal('1.0'))
        with self.assertRaises(Exception):
            GroceryItem.objects.create(name="Potatoes", price=Decimal('1.0'))

    def test_max_length_for_name(self):
        item = GroceryItem(name="a" * 101)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_decimal_price_precision(self):
        item = GroceryItem.objects.create(name="Butter", price=Decimal('2.1234'))
        self.assertEqual(item.price, Decimal('2.12'))

    def test_toggle_availability(self):
        item = GroceryItem.objects.create(name="Ice Cream", availability=True)
        item.availability = False
        item.save()
        self.assertFalse(item.availability)
