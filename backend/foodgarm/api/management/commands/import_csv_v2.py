import csv

from django.conf import settings
from pathlib import Path
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_data_ingredient():

    with open(
        Path(settings.BASE_DIR, 'data', 'ingredients.csv'),
        encoding='utf-8',
        newline=''
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        id = 0
        for row in reader:
            id += 1
            Ingredient.objects.create(
                id=id,
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
