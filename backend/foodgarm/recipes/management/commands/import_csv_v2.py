import csv

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_data_ingredient():

    with open(
        Path(settings.BASE_DIR, 'data', 'ingredients.csv'),
        encoding='utf-8',
        newline=''
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Ingredient.objects.create(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import_data_ingredient()
            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception:
            self.stdout.write(self.style.SUCCESS('Data imported fail'))
