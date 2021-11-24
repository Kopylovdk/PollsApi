from api.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    tables = [User]

    def handle(self, *args, **options):
        User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456')
        User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru', password='123456')
        print('Users: admin and anonymous are created with password 123456.\n')

        self.count_tables_data()
        # self.show_all_tables()

    def show_all_tables(self):
        for table in self.tables:
            print(table.objects.all())

    def count_tables_data(self):
        for table in self.tables:
            print(f'Количество строк в таблице {table.__name__}: {len(table.objects.all())}')