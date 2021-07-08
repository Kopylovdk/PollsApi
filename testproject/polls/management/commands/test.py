import datetime

import requests

# _________________ПОЛЬЗОВАТЕЛИ_____________________
data_user_reg = {'user': {
    'username': 'test',
    'password': '123456',
    "email": 'test@test.ru'
}}

result = requests.post('http://127.0.0.1:8000/api/users/register/', json=data_user_reg)
print(f'Регистрация {result.status_code}:\n{result.json()}')

data_user_auth = {'user': {
    'username': 'admin',
    'password': '123456'
}}

result = requests.post('http://127.0.0.1:8000/api/users/login/', json=data_user_auth)
# print(result.json())
headers = {"Authorization": f'Token {result.json()["user"]["token"]}'}

result = requests.get('http://127.0.0.1:8000/api/users/user/', headers=headers)
print(f'Данные пользователя {result.status_code}:\n{result.json()}')

data_user_update = {'user': {
    'first_name': 'test',
}}

result = requests.patch('http://127.0.0.1:8000/api/users/user/', headers=headers, json=data_user_update)
print(f'Обновленные пользователя {result.status_code}:\n{result.json()}')

# _________________ОПРОСЫ____________________

pol_create = {"polls": {
    "name": "test",
    "description": "test",
    "start_date": "2021-07-10",
    "end_date": "2021-08-11"
}}

result_create = requests.post('http://127.0.0.1:8000/api/polls/create/', headers=headers, json=pol_create)
print(f'Создание опроса {result_create.status_code}:\n{result_create.json()}')

pol_update = {"polls": {
    "name": "test после обновления",
}}

result = requests.patch(f'http://127.0.0.1:8000/api/polls/update/{result_create.json()["polls"]["id"]}',
                        headers=headers, json=pol_update)
print(f'Изменение опроса {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/polls/list/',
                      headers=headers, json=pol_update)
print(f'ВСЕ опросы {result.status_code}:\n{result.json()}')

result_get_all = requests.get(f'http://127.0.0.1:8000/api/polls/allActive/', headers=headers)
print(f'ВСЕ АКТИВНЫЕ опросы {result_get_all.status_code}:\n{result_get_all.json()}')

#
q_create_er = {"question": {
    "poll_id": result_create.json()["polls"]["id"],
    "question_type": "MANY_ANSWERS",
    "question_text": "Тестовое создание без вариантов ответа"
},
}

result = requests.post(f'http://127.0.0.1:8000/api/questions/', headers=headers, json=q_create_er)
print(f'Создание вопроса ОШИБКА {result.status_code}:\n{result.json()}')

q_create_m = {"question": {
    "poll_id": result_create.json()["polls"]["id"],
    "question_type": "MANY_ANSWERS",
    "question_text": "Тестовое создание c вариантами ответа"
},
    'question_options': ['test 1', 'test 2', 'test 3']
}

result_m = requests.post(f'http://127.0.0.1:8000/api/questions/', headers=headers, json=q_create_m)
print(f'Создание вопроса c вариантами ответов {result_m.status_code}:\n{result_m.json()}')

q_create_t = {"question": {
    "poll_id": result_create.json()["polls"]["id"],
    "question_type": "TEXT_ANSWER",
    "question_text": "Тестовое создание без вариантов ответа"
},

}

result_t = requests.post(f'http://127.0.0.1:8000/api/questions/', headers=headers, json=q_create_t)
print(f'Создание вопроса БЕЗ вариантов ответа {result_t.status_code}:\n{result_t.json()}')

q_update = {"question": {
    "question_text": "Изменение текста вопроса",
}}

result = requests.patch(f'http://127.0.0.1:8000/api/questions/{result_m.json()["question"]["id"]}',
                        headers=headers, json=q_update)
print(f'Изменение вопроса {result.status_code}:\n{result.json()}')

qo_create = {"question_options": {
    "question_answer": "Тестовое добавление варианта ответа"
}}

qo_result = requests.post(f'http://127.0.0.1:8000/api/questionOptions/{result_m.json()["question"]["id"]}',
                          headers=headers, json=qo_create)
print(f'Создание варианта ответа {qo_result.status_code}:\n{qo_result.json()}')

qo_update = {"question_options": {
    "question_answer": "Тестовое изменение"
}}

result = requests.patch(f'http://127.0.0.1:8000/api/questionOptions/{qo_result.json()["question_options"]["id"]}',
                        headers=headers, json=qo_update)
print(f'Изменение варианта ответа {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/polls/{result_create.json()["polls"]["id"]}', headers=headers)
print(f'Конкретный опрос {result.status_code}:\n{result.json()}')

data_user_auth = {'user': {
    'username': 'test',
    'password': '123456',
}}

result = requests.post('http://127.0.0.1:8000/api/users/login/', json=data_user_auth)
# print(result.json())
headers = {"Authorization": f'Token {result.json()["user"]["token"]}'}

user_answer = {"answers": {
    "poll_id": result_create.json()["polls"]["id"],
    "question_id": result_m.json()["question"]["id"],
    "question_option_id": [result_m.json()["question_options"][0]["id"],
                           result_m.json()["question_options"][1]["id"],
                           result_m.json()["question_options"][2]["id"]],
}
}
print(f'{user_answer=}')
result = requests.post(f'http://127.0.0.1:8000/api/users/answers/',
                       headers=headers, json=user_answer)
print(f'Создание 1 варианта ответа {result.status_code}:\n{result.json()}')

user_answer_2 = {"answers": {
    "poll_id": result_create.json()["polls"]["id"],
    "question_id": result_t.json()["question"]["id"],
    "user_answer": "Какой-то ОТВЕТ"}
}

print(f'{user_answer_2=}')
result = requests.post(f'http://127.0.0.1:8000/api/users/answers/',
                       headers=headers, json=user_answer_2)
print(f'Создание 2 варианта ответа {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/users/answers/', headers=headers)
print(f'Все ответы пользователя {result.status_code}:\n{result.json()}')

result = requests.get(f'http://127.0.0.1:8000/api/users/answers/')
print(f'Все ответы пользователя ОШИБКА {result.status_code}:\n{result.json()}')
