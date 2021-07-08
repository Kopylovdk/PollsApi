from django.core.management import BaseCommand
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_path = os.getcwd()
        apps_to_clear_migrations = ['api', 'polls']

        for app in apps_to_clear_migrations:
            path = os.path.join(current_path, f'{app}\\migrations')
            self.remove_files(path)
            print(f'Миграции для {app} очищены.')

        db_path = os.path.join(current_path, 'test.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
            print('База данны удалена.\n')

        print(os.popen('py manage.py makemigrations').read())
        print(os.popen('py manage.py migrate').read())

    def remove_files(self, path):
        for file in os.listdir(path):
            filepath = os.path.join(path, file)
            if file != '__init__.py' and '.gitkeep' \
                    and os.path.isfile(filepath):
                os.remove(filepath)
