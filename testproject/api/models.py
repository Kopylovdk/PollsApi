import jwt
from django.contrib.auth.models import AbstractUser

from main import settings


class User(AbstractUser):
    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя
        """
        token = jwt.encode({'id': self.pk}, settings.SECRET_KEY, algorithm='HS256')
        return token
