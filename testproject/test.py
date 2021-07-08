import requests

# _________________ПОЛЬЗОВАТЕЛИ_____________________
# data_user_reg = {'user': {
#     'username': 'test',
#     'password': '123456',
#     "email": 'test@test.ru'
# }}

# result = requests.post('http://127.0.0.1:8000/api/users/register/', json=data_user_reg)
# print(f'Регистрация {result.status_code}:\n{result.json()}')

data_user_auth = {'user': {
    'username': 'test',
    'password': '123456'
}}

result = requests.post('http://127.0.0.1:8000/api/users/login/', json=data_user_auth)
headers = {"Authorization": f'Token {result.json()["user"]["token"]}'}

# result = requests.get('http://127.0.0.1:8000/api/users/user/', headers=headers)
# print(f'Данные пользователя {result.status_code}:\n{result.json()}')

# data_user_update = {'user': {
#     'first_name': 'test',
# }}

# result = requests.patch('http://127.0.0.1:8000/api/users/user/', headers=headers, json=data_user_update)
# print(f'Обновленные пользователя {result.status_code}:\n{result.json()}')

# _________________ОПРОСЫ____________________

pol_create = {"polls": {
    "name": "test",
    "description": "test",
    "start_date": "2021-07-08",
    "end_date": "2021-07-15"
}}

result_create = requests.post('http://127.0.0.1:8000/api/polls/create/', headers=headers, json=pol_create)
print(f'Создание опроса {result_create.status_code}:\n{result_create.json()}')

pol_update = {"polls": {
    "name": "test после обновления",
}}

result = requests.patch(f'http://127.0.0.1:8000/api/polls/update/{result_create.json()["polls"]["id"]}', headers=headers, json=pol_update)
print(f'Изменение опроса {result.status_code}:\n{result.json()}')

