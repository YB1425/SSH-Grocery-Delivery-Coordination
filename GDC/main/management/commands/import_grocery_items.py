import csv
from django.core.management.base import BaseCommand
from main.models import GroceryItem  # Replace 'main' with your actual app name

class Command(BaseCommand):
    help = 'Import grocery items from a CSV file'

    def handle(self, *args, **kwargs):
        with open('C:/Users/Yasser/iCloudDrive/Documents/Misc/Programming Projects/SEPP/SSH-Grocery-Delivery-Coordination/GDC/cleaned_supermarket_80_items.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                GroceryItem.objects.create(
                    name=row['Product Name'],  # Map 'Product Name' to the 'name' field
                    description=row['Description'],
                    price=row['Price'],
                    availability=True,  # Default availability
                    category=row['Category']
                )
        self.stdout.write(self.style.SUCCESS('Grocery items imported successfully!'))
