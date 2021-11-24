from django.core.management import BaseCommand
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(os.popen('py manage.py makemigrations').read())
        print(os.popen('py manage.py migrate').read())
