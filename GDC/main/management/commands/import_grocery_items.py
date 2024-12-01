import csv
import os
from django.core.management.base import BaseCommand
from main.models import GroceryItem 

class Command(BaseCommand):
    help = 'Import grocery items from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            required=True,
            help='The file path to the CSV file containing grocery items.'
        )

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv']

        # Ensure the file exists
        if not os.path.isfile(csv_file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {csv_file_path}'))
            return

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    
                    if row['category'] not in dict(GroceryItem.CATEGORY_CHOICES):
                        self.stderr.write(self.style.ERROR(
                            f"Invalid category '{row['category']}' for item '{row['name']}'"
                        ))
                        continue  

                    
                    GroceryItem.objects.create(
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                        availability=True,
                        category=row['category']
                    )
            self.stdout.write(self.style.SUCCESS('Grocery items imported successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing grocery items: {e}'))
