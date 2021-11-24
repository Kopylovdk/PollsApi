from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import User


class UserTest(APITestCase):
    def test_user_cru(self):
        # Create (register)
        data_user_reg = {'user': {
            'username': 'test',
            'password': '123456',
            "email": 'test@test.ru'
        }}
        response = self.client.post(reverse('api:register'), data_user_reg, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().username, 'test')
        user = User.objects.get(username='test')

        # Auth
        data_user_login = {'user': {
            'username': 'test',
            'password': '123456'
        }}
        result_login = self.client.post(reverse('api:login'), data_user_login, format='json')
        self.assertEqual(result_login.status_code, status.HTTP_200_OK)
        headers = f'Token {result_login.json()["user"]["token"]}'

        # Read
        db_user_data_get = {'user': {'email': user.email, 'username': user.username,
                                     'token': user.token,
                                     'first_name': user.first_name, 'last_name': user.last_name}
                            }
        result_user_get = self.client.get(reverse('api:data'), HTTP_AUTHORIZATION=headers, format='json')
        self.assertEqual(result_user_get.status_code, status.HTTP_200_OK)
        self.assertEqual(db_user_data_get, result_user_get.json())

        # Update
        data_user_update = {'user': {
            'first_name': 'test',
        }}
        result_user_update = self.client.patch(reverse('api:data'), HTTP_AUTHORIZATION=headers,
                                               json=data_user_update)
        db_user_data_get['user']['first_name'] = User.objects.get(username='test').first_name
        self.assertEqual(result_user_update.status_code, status.HTTP_200_OK)
        self.assertEqual(db_user_data_get, result_user_update.json())

