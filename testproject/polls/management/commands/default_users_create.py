from api.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456')
        User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru', password='123456')
        print('Users: admin and anonymous are created with password 123456.\n')
