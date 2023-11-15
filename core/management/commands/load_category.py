from django.core.management import BaseCommand
import csv
from django.conf import settings

from core.models import AdvertiseCategory


class Command(BaseCommand):
    help = "Seed category names from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        datafile = settings.BASE_DIR / 'advertise_category.csv'
        file_path = kwargs['file_path']
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                for row in reader:
                    AdvertiseCategory.objects.get_or_create(category_name=row[0])
                self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS('Data imported fail ' + e.__str__()))
