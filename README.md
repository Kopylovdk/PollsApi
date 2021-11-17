# API для проведения опросов.

#### Базовая документация к проекту

Основные системные требования:
* Разработано на python 3.9 
* Зависимости (Python) из requirements.txt


### Скачиваем содержимое репозитория.
### Установка необходимого ПО
```
pip install -r requirements.txt
``` 
#### Возможно запустить файл run.bat - В результате будут проделаны все действия, указанные ниже и база данных будет наполнена тестовыми данными.
```
папка проекта/run.bat
```
#### Создание миграций, применение миграций. Внимание, в этом случае база данных будет пустая.
```
python manage.py makemigrations
python manage.py migrate
```
#### Обязательно нужно создать суперпользователя и пользователя с username = "anonymous" (это необходимо, чтобы не авторизованные пользователи могли проходить опросы)
```
python manage.py createsuperuser
python manage.py createuser
```
#### Пробуем запустить сервер
```
python manage.py runserver
```
#### Заполняет базу данных тестовыми данными (необязательно).
```
python manage.py fill_db
```
#### Удаляет базу данных и очищает миграции
```
python manage.py clear_and_migrate
```
После успешного запуска сервера возможно использовать API. Его описание ниже.

### Добавлен файл polls.management.commands.test.py
При запущенном сервере с тестовыми данными данный скрип проверяет работоспособность ВСЕХ URL.
После использования лучше почистить БД до выпуска в PROD.
___
## Описание работы API:
## Таблица со ссылками, методами и описаниями:
| URL  | Метод | Описание|
|----:|:----:|:----:|
| api/users/login/ | post | Авторизация пользователя
| api/users/register/ | post | Регистрация пользователя
| api/users/ | get | Получение данных о пользователе
| api/users/ | patch | Обновление данных пользователя
| api/users/polls/| get | Получение пройденных опросов пользователя с выбранными им вариантами ответа
| api/polls/ | post | Создание опроса
| api/polls/ | get | Получение списка ВСЕХ опросов (если пользователь superuser) или Активных опросов (если пользователь обычный или не зарегистрированный)
| api/polls/:id | patch | Изменение опроса
| api/polls/:id | get | Получение конкретного опроса
| api/polls/:id | delete | Активация / деактивация опроса
| api/questions/:id | post | Создание вопроса к определенному опросу
| api/questions/:id | patch | Обновление данных вопроса
| api/questions/:id | delete | Активация / деактивация вопроса
| api/questions/:id/answers/ | post | Отправка ответа пользователя на вопрос опроса
| api/question_options/:id | post | Создание вариантов ответа на определенный вопрос
| api/question_options/:id | patch | Обновление данных варианта ответа на вопрос
| api/question_options/:id | delete | Активация / деактивация ответа на вопрос
_____
### Пользователи:
#### Регистрация для пользователя:
Ссылка: ```/api/users/register/```
Метод:``` post ```
На вход принимает json вида:
```json
{"user": {
    "username": "str",
    "password": "str",
    "email": "str" }}
```
При успешном создании пользователя вернется статус HTTP_201_Created и все данные пользователя.

#### Авторизация для пользователя:
Ссылка: ```/api/users/login/```
Метод: ```post```
На вход принимает json вида:
```json
{"user": {
    "username": "str",
    "password": "str"
}}
```
При успешной авторизации пользователя вернется статус HTTP_200_OK и json вида:
```json
{"user": {
    "username": "str",
    "token": "str"
}}
```
Дальнейшая авторизация при работе с API для авторизированного пользователя будет
осуществляться при передаче token в headers в следующем виде:
```json
{"Authorization": "Token USER_TOKEN"}
```
#### Изменение данных пользователя:
Ссылка: ```/api/users/```
Метод: ```patch```
На вход принимает dict вида:
```json
{"user": {
    "email": "str",
    "first_name": "str",
    "last_name": "str",
    "username": "str",
    "password": "str"
}}
```
Возможно частичное изменение значений полей, передавать ВСЕ данные для изменения одного поля не нужно.
При успешном изменении пользователя вернется статус HTTP_200_OK и json с измененными данными.

#### Получение данных пользователя:
Ссылка: ```/api/users/```
Метод: ```get```
Возвращает json со всеми данными пользователя следующего вида:
```json
{"user": {
    "email": "str",
    "first_name": "str",
    "last_name": "str",
    "username": "str",
    "password": "str"
}}
```
### ВНИМАНИЕ!!! 
- Создание опросов (включая вопросы и ответы на них), их изменение и деактивация доступна только Суперпользователю
- Отвечать на опросы могут:
   - Авторизованные пользователи 
   - НЕ авторизованные пользователи (в этом случае headers должен отсутствовать 
   и будет автоматически подставлен пользователь anonymous)
- Получить данные о пройденных опросах могут ТОЛЬКО авторизованные пользователи, 
   которые отвечали на вопросы АВТОРИЗОВАННЫМИ.

___
#### Создание опроса:
Ссылка: ```/api/polls/```
Метод: ```post```
На вход принимает json вида:
```json
{"polls": {
    "name": "str",
    "description": "str",
    "start_date": "date(yyyy-mm-dd)",
    "end_date": "date(yyyy-mm-dd)"
}}
```
При успешном создании опроса вернется статус HTTP_201_CREATED и json с созданным опросом следующего вида:
```json
{"polls": {
    "id": "int",
    "name": "str",
    "description": "str",
    "start_date": "date(yyyy-mm-dd)",
    "end_date": "date(yyyy-mm-dd)",
    "is_active": "bool"
}}
```

#### Изменение опроса:
Ссылка: ```/api/polls/:id```
Метод: ```patch```
На вход принимает json вида, id опроса в url:
```json
{"polls": {
    "name": "str",
    "description": "str",
    "end_date": "date(yyyy-mm-dd)"
}}
```
Возможно частичное изменение значений полей, передавать ВСЕ данные для изменения одного поля не нужно.
При успешном выполнении запроса вернется статус HTTP_200_OK и json с измененными данными.

#### Активация / деактивация опроса:
Ссылка: ```/api/polls/:id```
Метод: ```delete```
id опроса в URL

При успешном выполнении запроса вернется статус HTTP_200_OK и json с данными вида
```
{'detail': 'Active change to True'}.
```

### ВНИМАНИЕ!!!!
- Изменить Дату старта опроса после создания опроса НЕВОЗМОЖНО.
- Изменение АКТИВНОСТИ опроса влечет за собой изменение активности ВОПРОСОВ,
   относящихся к этому ОПРОСУ и ОТВЕТОВ на ВОПРОСЫ, относящихся к соответствующим ВОПРОСАМ. 

#### Получение списка ВСЕХ опросов:
Ссылка: ```/api/polls/```
Метод: ```get```
*__Только для супер пользователя.__*
При успешном выполнении запроса вернется статус HTTP_200_OK и json со всеми опросами следующего вида:
```json
{"polls":[{
    "id": "int",
    "name": "str",
    "description": "str",
    "start_date": "date(yyyy-mm-dd)",
    "end_date": "date(yyyy-mm-dd)",
    "is_active": "bool"}]
}
```
#### Получение списка активных опросов:
Ссылка: ```/api/polls/```
Метод: ```get```
*__Доступно для ВСЕХ НЕ суперпользователей (включая незарегистрированных).__*
При успешном выполнении запроса вернется статус HTTP_200_OK и json со всеми АКТИВНЫМИ опросами следующего вида:
```json
{"polls":[{
    "id": "int",
    "name": "str",
    "description": "str",
    "start_date": "date(yyyy-mm-dd)",
    "end_date": "date(yyyy-mm-dd)",
    "is_active": "bool"}]
}

```
#### Получение конкретного АКТИВНОГО опроса:
Ссылка: ```/api/polls/:id```
Метод: ```get```
*__Доступно для ВСЕХ пользователей.__*
id нужного опроса в url:

В случае попытки получить неактивный опрос вернется статус HTTP_404_NOT_FOUND.
При успешном выполнении запроса вернется статус HTTP_200_OK и json вида:
```json
{"poll": 
    {
      "id": "int",
      "name": "str",
      "description": "str",
      "start_date": "date(yyyy-mm-dd)",
      "end_date": "date(yyyy-mm-dd)",
      "is_active": "bool"
    },
    "questions": 
    [
      {
        "question": {
          "id": "int",
          "question_type": "str (choices)",
          "question_text": "str",
          "is_active": "bool",
          "poll_id": "int"
        },
        "question_options": [{
            "id": "int",
            "question_answer": "str",
            "is_active": "bool",
            "question_id": "int"}]
      }
    ]
}
```
Json содержит информацию о конкретном опросе и в "questions" содержит пары: вопрос и ответы на вопрос(при наличии),
относящиеся к этому опросу

#### Создание вопроса:
Ссылка: ```api/questions/:id```
Метод: ```post```

На вход принимает json вида, id ОПРОСА в url:
```json
{"question": {
    "poll_id": "int",
    "question_type": "str (choices)",
    "question_text": "str"
     },
"question_options": ["str", "str", "str"]
}
```
При успешном выполнении запроса вернется статус HTTP_201_CREATED и json с созданными данными.
В случае передачи не существующего ID опроса вернется HTTP_404_NOT_FOUND.

### ВНИМАНИЕ!!!!
- Поле question_type может иметь 3 значения:
    - MANY_ANSWERS - Означает, что на вопрос может быть несколько ответов, выбранных пользователем из списка.
    - ONE_ANSWER - Означает, что на вопрос должен быть один ответ, выбранный пользователем из списка.
    - TEXT_ANSWER - Означает, что на вопрос должен быть ТЕКСТОВЫЙ ответ от пользователя
- Если тип вопроса TEXT_ANSWER, то question_options можно не указывать.
#### Обновление вопроса:
Ссылка: ```api/questions/:id```
Метод: ```patch```
На вход принимает json вида, id вопроса в url:
```json
{"question": {
    "poll_id": "int",
    "question_type": "str (CHOICE)",
    "question_text": "str"
}}
```
Возможно частичное изменение значений полей, передавать ВСЕ данные для изменения одного поля не нужно.
При успешном выполнении запроса вернется статус HTTP_200_OK и json с измененными данными.
В случае передачи не существующего ID опроса вернется HTTP_404_NOT_FOUND.

#### Активация / деактивация вопроса:
Ссылка: ```api/questions/:id```
Метод: ```delete```
id вопроса в URL

При успешном выполнении запроса вернется статус HTTP_200_OK и json с данными вида
```
{'detail': 'Active change to True'}.
```

### ВНИМАНИЕ!!!!
- Изменение АКТИВНОСТИ Вопроса влечет за собой изменение активности ответов,
   относящихся к этому ВОПРОСУ. 

#### Создание варианта ответа на определенный вопрос
Ссылка: ```api/question_options/:id```
Метод: ```post```
На вход принимает json вида, id ВОПРОСА в url:
```json
{"question_options": [
         {
           "question_answer": "str"}
      ]
}
```
Список может содержать неограниченное количество вариантов ответа.
При успешном выполнении запроса вернется статус HTTP_201_CREATED и json c созданными данными
В случае передачи не существующего ID ВОПРОСА вернется HTTP_404_NOT_FOUND.

#### Изменение варианта ответа на определенный вопрос
Ссылка: ```api/question_options/:id```
Метод: ```patch```
На вход принимает json вида, id ВАРИАНТА ОТВЕТА в url:
```json
{
"question_options": 
        {
         "question_id": "int",
         "question_answer": "str"}
    
}
```

При успешном выполнении запроса вернется статус HTTP_200_OK и json c измененными данными:
В случае передачи не существующего ID ВОПРОСА или ВАРИАНТА ОТВЕТА вернется HTTP_404_NOT_FOUND.

#### Активация / деактивация варианта ответа на вопрос:
Ссылка: ```api/question_options/:id```
Метод: ```delete```
id ВАРИАНТА ОТВЕТА в url

При успешном выполнении запроса вернется статус HTTP_200_OK и json с данными вида
```
{'detail': 'Active change to True'}.
```

#### Ответ пользователя на опрос:

Ссылка: ```api/questions/:q_id/answers/```
Метод: ```post```
*__Доступно для ВСЕХ пользователей.__*
В URL ID ВОПРОСА
В случае передачи не существующего ВОПРОСА или ВАРИНТА ОТВЕТА вернется HTTP_404_NOT_FOUND. Ответ записан НЕ БУДЕТ.
На вход принимает json вида:
```json
{"answers": {
        "question_option_id": ["int", "int", "int"],
        "user_answer": "str"}
}
```
Подразумевается, что пользователь будет проходить опрос передавая ответы на вопросы последовательно.
При успешном выполнении запроса вернется статус HTTP_201_CREATED и json вида:
```json
{"answers": "Data saved"}
```

#### Запрос информации о пройденных опросах:
Ссылка: ```api/users/polls/```
Метод: ```get```
Доступно ТОЛЬКО АВТОРИЗОВАННОМУ пользователю. 
При попытке получить данные без авторизации вернется статус HTTP_403_FORBIDDEN и json вида:
```json
{"detail": "You do not have permission to perform this action."}
```
При успешном выполнении запроса вернется статус HTTP_200_OK и json вида:
```json
{"polls": [
  {"poll":
    {"id": "int",
     "name": "str",
     "description": "str",
     "start_date": "date(yyyy-mm-dd)",
     "end_date": "date(yyyy-mm-dd)", 
     "is_active": "bool"
    },
     "questions": [
       {"question": {"id": "int",
         "question_type": "str (CHOICE)",
         "question_text": "str",
         "is_active": "bool", 
         "poll_id": "int"},
       "answers": [
         "Либо str либо dict с ответом"]
       }]
  }
]}
```
Json содержит информацию по пройденным пользователем опросам с вопросами и ответами пользователя на них.
