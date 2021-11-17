import requests
# Для проверки исключений необходимо изменить username с admin на test (строка 14)
print('_________________ПОЛЬЗОВАТЕЛИ_____________________')
print('__________РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ________________')
data_user_reg = {'user': {
    'username': 'test',
    'password': '123456',
    "email": 'test@test.ru'
}}

result = requests.post('http://127.0.0.1:8000/api/users/register/', json=data_user_reg)
print(f'Регистрация {result.status_code}:\n{result.json()}')


print('__________АВТОРИЗАЦИЯ СУПЕР ПОЛЬЗОВАТЕЛЯ________________')

data_user_admin_auth = {'user': {
    'username': 'admin',
    'password': '123456'
}}

result = requests.post('http://127.0.0.1:8000/api/users/login/', json=data_user_admin_auth)
headers = {"Authorization": f'Token {result.json()["user"]["token"]}'}
print(f'Результат авторизации супер пользователя {result.status_code}:\n{result.json()}')

result = requests.get('http://127.0.0.1:8000/api/users/', headers=headers)
print(f'Данные пользователя {result.status_code}:\n{result.json()}')

data_user_update = {'user': {
    'first_name': 'test',
}}

result = requests.patch('http://127.0.0.1:8000/api/users/', headers=headers, json=data_user_update)
print(f'Обновленные пользователя {result.status_code}:\n{result.json()}')


print('_________________ОПРОСЫ____________________')


pol_create = {"polls": {
    "name": "test",
    "description": "test",
    "start_date": "2021-07-10",
    "end_date": "2021-08-11"
}}

result_create = requests.post('http://127.0.0.1:8000/api/polls/', headers=headers, json=pol_create)
print(f'Создание опроса {result_create.status_code}:\n{result_create.json()}')

pol_update = {"polls": {
    "description": "test update",
}}

result = requests.patch(f'http://127.0.0.1:8000/api/polls/'
                        f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                        headers=headers, json=pol_update)
print(f'Изменение опроса {result.status_code}:\n{result.json()}')

result = requests.delete(f'http://127.0.0.1:8000/api/polls/'
                         f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                         headers=headers)
print(f'Изменение активности ОПРОСА - ОК {result.status_code}:\n{result.json()}')


result = requests.delete(f'http://127.0.0.1:8000/api/polls/50', headers=headers)
print(f'Изменение активности ОПРОСА - Error {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/polls/', headers=headers)
print(f'ВСЕ опросы {result.status_code}:\n{result.json()}')


print('_________________Вопросы____________________')


q_create_er = {"question": {
    "question_type": "MANY_ANSWERS",
    "question_text": "Тестовое создание без вариантов ответа"
}}

result = requests.post(f'http://127.0.0.1:8000/api/questions/'
                       f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                       headers=headers, json=q_create_er)
print(f'Создание вопроса ОШИБКА {result.status_code}:\n{result.json()}')

q_create_m = {"question": {
    "question_type": "MANY_ANSWERS",
    "question_text": "Тестовое создание c вариантами ответа"
},
    'question_options': ['test 1', 'test 2', 'test 3']
}

result_m = requests.post(f'http://127.0.0.1:8000/api/questions/'
                         f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                         headers=headers, json=q_create_m)
print(f'Создание вопроса c вариантами ответов {result_m.status_code}:\n{result_m.json()}')

q_create_t = {"question": {
    "question_type": "TEXT_ANSWER",
    "question_text": "Тестовое создание без вариантов ответа"
}
}

result_t = requests.post(f'http://127.0.0.1:8000/api/questions/'
                         f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                         headers=headers, json=q_create_t)
print(f'Создание вопроса БЕЗ вариантов ответа {result_t.status_code}:\n{result_t.json()}')

q_update = {"question": {
    "question_text": "Изменение текста вопроса",
}}

result = requests.patch(f'http://127.0.0.1:8000/api/questions/'
                        f'{result_m.json()["question"]["id"] if result_m.status_code == 201 else 1}',
                        headers=headers, json=q_update)
print(f'Изменение вопроса {result.status_code}:\n{result.json()}')


result = requests.delete(f'http://127.0.0.1:8000/api/questions/'
                         f'{result_m.json()["question"]["id"] if result_m.status_code == 201 else 1}',
                         headers=headers)
print(f'Изменение активности ВОПРОСА - ОК {result.status_code}:\n{result.json()}')


result = requests.delete(f'http://127.0.0.1:8000/api/questions/1000', headers=headers)
print(f'Изменение активности ВОПРОСА - Error {result.status_code}:\n{result.json()}')


print('_________________Ответы на вопрос____________________')


qo_create = {"question_options": {
    "question_answer": "Тестовое добавление варианта ответа"
}}

qo_result = requests.post(f'http://127.0.0.1:8000/api/question_options/'
                          f'{result_m.json()["question"]["id"] if result_m.status_code == 201 else 1}',
                          headers=headers, json=qo_create)
print(f'Создание варианта ответа {qo_result.status_code}:\n{qo_result.json()}')

qo_update = {"question_options": {
    "question_answer": "Тестовое изменение"
}}

result = requests.patch(f'http://127.0.0.1:8000/api/question_options/'
                        f'{qo_result.json()["question_options"]["id"] if qo_result.status_code == 201 else 1}',
                        headers=headers, json=qo_update)
print(f'Изменение варианта ответа {result.status_code}:\n{result.json()}')

data_user_auth = {'user': {
    'username': 'test',
    'password': '123456',
}}

result = requests.delete(f'http://127.0.0.1:8000/api/question_options/'
                         f'{qo_result.json()["question_options"]["id"] if qo_result.status_code == 201 else 1}',
                         headers=headers)
print(f'Изменение активности ОТВЕТА НА ВОПРОС - ОК {result.status_code}:\n{result.json()}')

result = requests.delete(f'http://127.0.0.1:8000/api/question_options/10000', headers=headers)
print(f'Изменение активности ОТВЕТА НА ВОПРОС - Error {result.status_code}:\n{result.json()}')


print('_________________Авторизация обычного пользователя____________________')

data_user_auth = {'user': {
    'username': data_user_admin_auth.get('user').get('username'),
    'password': data_user_admin_auth.get('user').get('password')
}}

result = requests.post('http://127.0.0.1:8000/api/users/login/', json=data_user_auth)
headers = {"Authorization": f'Token {result.json()["user"]["token"]}'}
print(f'Результат авторизации обычного пользователя {result.status_code}:\n{result.json()}')

print('_________________Действия обычного пользователя____________________')


result_get_all = requests.get(f'http://127.0.0.1:8000/api/polls/', headers=headers)
print(f'ВСЕ АКТИВНЫЕ опросы {result_get_all.status_code}:\n{result_get_all.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/polls/'
                      f'{result_create.json()["polls"]["id"] if result_create.status_code == 201 else 1}',
                      headers=headers)
print(f'Конкретный опрос {result.status_code}:\n{result.json()}')

user_answer = {"answers": {
    "question_option_id": [result_m.json()["question_options"][0]["id"] if result_m.status_code == 201 else 1,
                           result_m.json()["question_options"][1]["id"] if result_m.status_code == 201 else 1,
                           result_m.json()["question_options"][2]["id"] if result_m.status_code == 201 else 1],
}
}
result = requests.post(f'http://127.0.0.1:8000/api/questions/'
                       f'{result_m.json()["question"]["id"] if result_m.status_code == 201 else 1}/answers/',
                       headers=headers, json=user_answer)
print(f'Создание 1 варианта ответа {result.status_code}:\n{result.json()}')

user_answer_2 = {"answers": {
    "user_answer": "Какой-то ОТВЕТ"}
}

result = requests.post(f'http://127.0.0.1:8000/api/questions/'
                       f'{result_t.json()["question"]["id"] if result_t.status_code == 201 else 1}/answers/',
                       headers=headers, json=user_answer_2)
print(f'Создание 2 варианта ответа {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/users/polls/', headers=headers)
print(f'Все ответы пользователя {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/users/polls/')
print(f'Все ответы пользователя ОШИБКА {result.status_code}:\n{result.json()}')

result = requests.delete(f'http://127.0.0.1:8000/api/question_options/10000', headers=headers)
print(f'Изменение активности ОТВЕТА НА ВОПРОС обычным пользователем - Error {result.status_code}:\n{result.json()}')
