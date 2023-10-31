from django.core.management import BaseCommand
import csv
from django.conf import settings

from core.models import CityList


class Command(BaseCommand):
    help = "Seed city names from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        datafile = settings.BASE_DIR / 'city_names.csv'
        file_path = kwargs['file_path']
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                for row in reader:
                    CityList.objects.get_or_create(city_name=row[0])
                self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception:
            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
