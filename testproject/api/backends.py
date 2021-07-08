import jwt
from django.conf import settings
from api.models import User
from rest_framework import authentication, exceptions


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Некорректный заголовок токена, в заголовке передан один элемент
            return None

        elif len(auth_header) > 2:
            # Некорректный заголовок токена, какие-то лишние пробельные символы
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # Префикс заголовка не тот, который мы ожидали - отказ.
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Попытка аутентификации с предоставленными данными. Если успешно -
        вернуть пользователя и токен, иначе - сгенерировать исключение.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(pk=payload['id'])
            if not user.is_active:
                msg = 'Данный пользователь деактивирован.'
                raise exceptions.AuthenticationFailed(msg)
            return (user, token)
        except Exception:
            msg = 'Ошибка аутентификации. Невозможно декодировать токен.'
            raise exceptions.AuthenticationFailed(msg)
        except User.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg)

