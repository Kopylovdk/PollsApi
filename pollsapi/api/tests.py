import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import User, Poll, Question, QuestionOptions, UsersAnswers


class UserCreateTest(APITestCase):
    def setUp(self):
        self.data = {'user': {
            'username': 'test',
            'password': '123456',
            "email": 'test@test.ru'
        }}

    def test_user_create(self):
        result = self.client.post(reverse('api:register'), self.data, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in result.json()['user'])
        self.assertEqual(User.objects.get(username=self.data.get('user').get('username')).username, 'test')


class UserAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.ru', password='123456')
        self.data_login = {'user': {
            'username': 'test',
            'password': '123456'
        }}
        self.headers = f'Token {self.user.token}'

    def test_user_login(self):
        result = self.client.post(reverse('api:login'), self.data_login, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.token, result.json()["user"]["token"])


class UserGetDataTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.ru', password='123456')
        self.headers = f'Token {self.user.token}'
        self.correct_data = {'user': {'email': self.user.email,
                                      'username': self.user.username,
                                      'token': self.user.token,
                                      'first_name': self.user.first_name,
                                      'last_name': self.user.last_name}
                             }

    def test_user_get_data(self):
        result = self.client.get(reverse('api:data'), HTTP_AUTHORIZATION=self.headers, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(self.correct_data, result.json())


class UserUpdateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.ru', password='123456')
        self.headers = f'Token {self.user.token}'
        self.correct_data = {'user': {'email': self.user.email,
                                      'username': self.user.username,
                                      'token': self.user.token,
                                      'first_name': self.user.first_name,
                                      'last_name': self.user.last_name}
                             }
        self.data_update = {'user': {'first_name': 'test'}}

    def test_user_update(self):
        result = self.client.patch(reverse('api:data'), self.data_update, HTTP_AUTHORIZATION=self.headers,
                                   format='json')
        self.correct_data['user']['first_name'] = User.objects.get(username='test').first_name
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(self.correct_data, result.json())


class PollsCreateReadTest(APITestCase):
    def setUp(self):
        self.url = reverse('api:poll')
        self.user_token = f"Token {User.objects.create_user(username='test', email='test@test.ru', password='123456').token}"
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        data_add_to_tst_db()
        self.polls = Poll.objects.all()
        self.url_pk = reverse('api:poll_pk', kwargs={'pk': self.polls[0].id})
        self.new_poll_data = {"polls": {"name": "test",
                                        "description": "test",
                                        "start_date": datetime.date.today(),
                                        "end_date": datetime.date.today() + datetime.timedelta(days=2)
                                        }
                              }

    def test_poll_superuser_create(self):
        result = self.client.post(self.url, self.new_poll_data,
                                  HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in result.json()['polls'])

    def test_poll_user_create(self):
        result = self.client.post(self.url, self.new_poll_data,
                                  HTTP_AUTHORIZATION=self.user_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_poll_get_one(self):
        result = self.client.get(self.url_pk, HTTP_AUTHORIZATION=self.user_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('poll' in result.json())
        self.assertTrue('questions' in result.json())
        self.assertTrue('question_options' in result.json()['questions'][0])

    def test_polls_superuser_get_all(self):
        result = self.client.get(self.url, HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in result.json()['polls'][0])
        self.assertEqual(len(self.polls), len(result.json()['polls']))

    def test_polls_user_get_all_active(self):
        result = self.client.get(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in result.json()['polls'][0])
        self.assertEqual(len(self.polls.filter(is_active=True)), len(result.json()['polls']))


class PollUpdateDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.anonymous_token = f"Token {User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru', password='123456').token}"
        self.poll_data = {'name': 'Опрос номер 1',
                          'description': 'Описание опроса номер 1',
                          'start_date': datetime.date.today(),
                          'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.poll = Poll.objects.create(**self.poll_data)
        self.url_pk = reverse('api:poll_pk', kwargs={'pk': self.poll.id})
        self.url_pk_bad = reverse('api:poll_pk', kwargs={'pk': 10000})
        self.correct_poll_data = {'polls': {'id': self.poll.id,
                                            'is_active': self.poll.is_active,
                                            'name': self.poll.name,
                                            'description': self.poll.description,
                                            'start_date': self.poll.start_date,
                                            'end_date': self.poll.end_date}}
        self.poll_data_update = {"polls": {"description": "test update"}}

    def test_poll_no_data(self):
        result = self.client.patch(self.url_pk,
                                   HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_poll_bad_pk(self):
        result = self.client.patch(self.url_pk_bad, self.poll_data_update,
                                   HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)

    def test_poll_superuser_update(self):
        result = self.client.patch(self.url_pk, self.poll_data_update,
                                   HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.correct_poll_data['polls']['description'] = Poll.objects.get(id=self.poll.id).description
        self.correct_poll_data['polls']['id'] = self.poll.id
        self.correct_poll_data['polls']['is_active'] = True
        span = result.json()['polls']['start_date'].split('-')
        result.json()['polls']['start_date'] = datetime.date(int(span[0]), int(span[1]), int(span[2]))
        span = result.json()['polls']['end_date'].split('-')
        result.json()['polls']['end_date'] = datetime.date(int(span[0]), int(span[1]), int(span[2]))
        self.assertEqual(self.correct_poll_data, result.json())

    def test_poll_user_update(self):
        result = self.client.patch(self.url_pk, self.poll_data_update,
                                   HTTP_AUTHORIZATION=self.anonymous_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_poll_user_delete_bad_data(self):
        result = self.client.delete(self.url_pk, self.poll_data_update,
                                    HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_poll_user_delete_not_allowed(self):
        result = self.client.delete(self.url_pk, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())
        result = self.client.delete(self.url_pk, format='json', HTTP_AUTHORIZATION=self.anonymous_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_poll_user_delete_bad_pk(self):
        result = self.client.delete(self.url_pk_bad, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)

    def test_poll_superuser_delete(self):
        result = self.client.delete(self.url_pk, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('detail' in result.json())
        self.assertFalse(Poll.objects.get(id=self.poll.id).is_active)


class QuestionCreateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.q_types = {'text': "TEXT_ANSWER",
                        'many': "CHOSE_ANSWER",
                        }
        self.new_p_data = {"name": "test",
                           "description": "test",
                           "start_date": datetime.date.today(),
                           "end_date": datetime.date.today() + datetime.timedelta(days=2)
                           }
        self.poll = Poll.objects.create(**self.new_p_data)
        self.new_p_data['is_active'] = False
        self.poll_de_act = Poll.objects.create(**self.new_p_data)
        self.url = reverse('api:question', kwargs={'pk': self.poll.id})
        self.new_q_data_bad = {"question": {"question_type": 'select from self.q_types in test',
                                            "question_text": "Тестовое создание"
                                            }
                               }
        self.new_q_data = {"question": {"question_type": 'select from self.q_types in test',
                                        "question_text": "Тестовое создание"
                                        },
                           'question_options': ['test 1', 'test 2', 'test 3']
                           }

    def test_create_question_no_auth_or_admin(self):
        result = self.client.post(self.url, self.new_q_data, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_create_question_bad_poll_id(self):
        result = self.client.post(reverse('api:question', kwargs={'pk': 10000}), self.new_q_data, format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_question_poll_deactivate(self):
        self.new_q_data["question"]["question_type"] = self.q_types['text']
        result = self.client.post(reverse('api:question', kwargs={'pk': self.poll_de_act.id}), self.new_q_data,
                                  format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_create_question_no_data(self):
        result = self.client.post(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_bad_data_no_question_option(self):
        self.new_q_data_bad["question"]["question_type"] = self.q_types['many']
        result = self.client.post(self.url, self.new_q_data_bad, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_bad_q_type(self):
        result = self.client.post(self.url, self.new_q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())
        self.assertTrue('question_type' in result.json()['errors'])

    def test_create_question_text_answer(self):
        self.new_q_data["question"]["question_type"] = self.q_types['text']
        del (self.new_q_data['question_options'])
        result = self.client.post(self.url, self.new_q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('question' in result.json())
        self.assertTrue('id' in result.json()['question'])
        q = Question.objects.get(id=result.json()['question']['id'])
        correct_data = {'question': {'id': q.id,
                                     'question_type': q.question_type,
                                     'question_text': q.question_text,
                                     'is_active': q.is_active,
                                     'poll_id': q.poll_id.id}}
        self.assertEqual(correct_data, result.json())

    def test_create_question_chose_answer(self):
        self.new_q_data["question"]["question_type"] = self.q_types['many']
        result = self.client.post(self.url, self.new_q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('question' in result.json())
        self.assertTrue('id' in result.json()['question'])
        self.assertTrue('question_options' in result.json())
        self.assertTrue('id' in result.json()['question_options'][0])
        q = Question.objects.get(id=result.json()['question']['id'])
        correct_data = {'question': {'id': q.id,
                                     'question_type': q.question_type,
                                     'question_text': q.question_text,
                                     'is_active': q.is_active,
                                     'poll_id': q.poll_id.id},
                        'question_options': []
                        }
        qo = QuestionOptions.objects.filter(question_id=q.id)

        for qo_i in qo:
            correct_data['question_options'].append({'id': qo_i.id, 'question_answer': qo_i.question_answer,
                                                     'is_active': qo_i.is_active, 'question_id': qo_i.question_id.id})

        self.assertEqual(correct_data, result.json())


class QuestionUpdateDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.q_types = {'text': "TEXT_ANSWER",
                        'many': "CHOSE_ANSWER",
                        }
        self.new_p_data = {"name": "test",
                           "description": "test",
                           "start_date": datetime.date.today(),
                           "end_date": datetime.date.today() + datetime.timedelta(days=2)
                           }
        self.poll = Poll.objects.create(**self.new_p_data)
        self.new_p_data['is_active'] = False
        self.poll_de_act = Poll.objects.create(**self.new_p_data)
        self.new_q_data = {"question": {"question_type": 'some',
                                        "question_text": "Тестовое создание",
                                        "poll_id": self.poll
                                        },
                           'question_options': ['test 1', 'test 2', 'test 3']
                           }
        self.new_q_data['question']["question_type"] = self.q_types.get('text')
        self.q_text = Question.objects.create(**self.new_q_data['question'])
        self.new_q_data['question']["question_type"] = self.q_types.get('many')
        self.q_many = Question.objects.create(**self.new_q_data['question'])
        self.update_data = 'data after update'
        del self.new_q_data['question']["poll_id"]

    def test_update_question_no_auth(self):
        self.new_q_data['question']["question_text"] = self.update_data
        result = self.client.patch(reverse('api:question', kwargs={'pk': self.q_many.id}), self.new_q_data,
                                   format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_update_question_no_data(self):
        result = self.client.patch(reverse('api:question', kwargs={'pk': self.q_many.id}),
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_update_question_bad_pk(self):
        self.new_q_data['question']["question_text"] = self.update_data
        result = self.client.patch(reverse('api:question', kwargs={'pk': 10000}), self.new_q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_update_question_chose_answer(self):
        self.new_q_data['question']["question_text"] = self.update_data
        result = self.client.patch(reverse('api:question', kwargs={'pk': self.q_many.id}), self.new_q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('question' in result.json())
        check = Question.objects.get(id=self.q_many.id)
        self.assertEqual(check.question_text, self.update_data)
        self.assertEqual(check.id, result.json()['question']['id'])

    def test_update_question_text_answer(self):
        self.new_q_data['question']["question_text"] = self.update_data
        result = self.client.patch(reverse('api:question', kwargs={'pk': self.q_many.id}), self.new_q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('question' in result.json())
        check = Question.objects.get(id=self.q_many.id)
        self.assertEqual(check.question_text, self.update_data)
        self.assertEqual(check.id, result.json()['question']['id'])

    def test_update_question_text_answer_poll_id(self):
        self.new_q_data['question']["poll_id"] = self.poll_de_act.id
        result = self.client.patch(reverse('api:question', kwargs={'pk': self.q_many.id}), self.new_q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_delete_question_no_auth(self):
        result = self.client.delete(reverse('api:question', kwargs={'pk': self.q_many.id}), data=self.new_q_data,
                                    format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_delete_question_with_data(self):
        result = self.client.delete(reverse('api:question', kwargs={'pk': self.q_many.id}), self.new_q_data,
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_delete_question_bad_pk(self):
        result = self.client.delete(reverse('api:question', kwargs={'pk': 100000}),
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_delete_question(self):
        result = self.client.delete(reverse('api:question', kwargs={'pk': self.q_many.id}),
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('detail' in result.json())


class QuestionOptionsCreateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        data_add_to_tst_db()
        self.url = reverse('api:question_options', kwargs={'pk': Question.objects.get(id=4).id})
        self.qo_data = {"question_options": [{"question_answer": "Тестовое добавление варианта ответа 10"},
                                             {"question_answer": "Тестовое добавление варианта ответа 11"}]
                        }
        self.to_create_q = {'poll_id': Poll.objects.get(id=1),
                            'question_type': 'CHOSE_ANSWER',
                            'question_text': 'Тест',
                            'is_active': False
                            }
        self.qo_deact_id = Question.objects.create(**self.to_create_q).id

    def test_create_question_options_no_auth(self):
        result = self.client.post(self.url, self.qo_data, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_create_question_options_bad_question_id(self):
        result = self.client.post(reverse('api:question_options', kwargs={'pk': 10000}), self.qo_data, format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_question_options_deact_question(self):
        result = self.client.post(reverse('api:question_options', kwargs={'pk': self.qo_deact_id}), self.qo_data,
                                  format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_create_question_no_data(self):
        result = self.client.post(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_options(self):
        result = self.client.post(self.url, self.qo_data,
                                  format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('question_options' in result.json())
        self.assertTrue('id' in result.json()['question_options'][0])


class QuestionOptionsUpdateDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        data_add_to_tst_db()
        self.data_to_update = {"question_options": {"question_answer": "Тестовое изменение варианта ответа"}}
        self.url = reverse('api:question_options', kwargs={'pk': QuestionOptions.objects.get(id=4).id})
        self.to_create_q = {'poll_id': Poll.objects.get(id=1),
                            'question_type': 'CHOSE_ANSWER',
                            'question_text': 'Тест',
                            'is_active': False
                            }
        self.qo_deact_id = Question.objects.create(**self.to_create_q).id

    def test_update_question_options_no_auth(self):
        result = self.client.patch(self.url, self.data_to_update, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_update_question_options_bad_question_option_id(self):
        result = self.client.patch(reverse('api:question_options', kwargs={'pk': 10000}), self.data_to_update, format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_question_no_data(self):
        result = self.client.patch(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    # TODO: Проверка, изменение, когда не активен варианта ответа и когда не активен Вопрос для этого варианта ответа
    # def test_update_question_options_deact_question(self):
    #     result = self.client.patch(reverse('api:question_options', kwargs={'pk': self.qo_deact_id}), self.data_to_update,
    #                               format='json', HTTP_AUTHORIZATION=self.admin_token)
    #     self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertTrue('errors' in result.json())
    #     print(result.json(), result.status_code)




# def test_question_options_crud(self):
# print(result.json(), result.status_code)
# pass

# def test_users_answers_crud(self):
#     pass
def data_add_to_tst_db():
    polls = [
        {'name': 'Опрос номер 1',
         'description': 'Описание опроса номер 1',
         'start_date': datetime.date.today(),
         'end_date': datetime.date.today() + datetime.timedelta(days=2)},
        {'name': 'Опрос номер 2',
         'description': 'Описание опроса номер 2',
         'start_date': datetime.date.today(),
         'end_date': datetime.date.today() + datetime.timedelta(days=4)},
        {'name': 'Опрос номер 3',
         'description': 'Описание опроса номер 3',
         'start_date': datetime.date.today(),
         'end_date': datetime.date.today() + datetime.timedelta(days=6)},
        {'name': 'Опрос номер 4',
         'description': 'Описание опроса номер 4 без вопросов',
         'start_date': datetime.date.today(),
         'end_date': datetime.date.today() + datetime.timedelta(days=6),
         'is_active': False},
        {'name': 'Опрос номер 5',
         'description': 'Описание опроса номер 5 только текстовые вопросы',
         'start_date': datetime.date.today(),
         'end_date': datetime.date.today() + datetime.timedelta(days=6)}
    ]

    for item in polls:
        Poll.objects.create(**item)

    TEXT = 'TEXT_ANSWER'
    CHOSE_ANSWER = 'CHOSE_ANSWER'
    pol = Poll.objects.all()

    questions = [
        {'poll_id': pol[0],
         'question_type': TEXT,
         'question_text': 'Вопрос 1 опроса 1 с текстовым ответом'},
        {'poll_id': pol[0],
         'question_type': TEXT,
         'question_text': 'Вопрос 2 опроса 1 с текстовым ответом'},
        {'poll_id': pol[0],
         'question_type': TEXT,
         'question_text': 'Вопрос 3 опроса 1 с текстовым ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 4 опроса 1 с одним правильным ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 5 опроса 1 с одним правильным ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 6 опроса 1 с одним правильным ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 7 опроса 1 с несколькими правильными ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 8 опроса 1 с несколькими правильными ответом'},
        {'poll_id': pol[0],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 9 опроса 1 с несколькими правильными ответом'},
        #  ОПРОС 2
        {'poll_id': pol[1],
         'question_type': TEXT,
         'question_text': 'Вопрос 1 опроса 2 с текстовым ответом'},
        {'poll_id': pol[1],
         'question_type': TEXT,
         'question_text': 'Вопрос 2 опроса 2 с текстовым ответом'},
        {'poll_id': pol[1],
         'question_type': TEXT,
         'question_text': 'Вопрос 3 опроса 2 с текстовым ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 4 опроса 2 с одним правильным ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 5 опроса 2 с одним правильным ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 6 опроса 2 с одним правильным ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 7 опроса 2 с несколькими правильными ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 8 опроса 2 с несколькими правильными ответом'},
        {'poll_id': pol[1],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 9 опроса 2 с несколькими правильными ответом'},
        #  ОПРОС 3
        {'poll_id': pol[2],
         'question_type': TEXT,
         'question_text': 'Вопрос 1 опроса 3 с текстовым ответом'},
        {'poll_id': pol[2],
         'question_type': TEXT,
         'question_text': 'Вопрос 2 опроса 3 с текстовым ответом'},
        {'poll_id': pol[2],
         'question_type': TEXT,
         'question_text': 'Вопрос 3 опроса 3 с текстовым ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 4 опроса 3 с одним правильным ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 5 опроса 3 с одним правильным ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 6 опроса 3 с одним правильным ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 7 опроса 3 с несколькими правильными ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 8 опроса 3 с несколькими правильными ответом'},
        {'poll_id': pol[2],
         'question_type': CHOSE_ANSWER,
         'question_text': 'Вопрос 9 опроса 3 с несколькими правильными ответом'},
        # Опрос 5
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 1 опроса 5 с текстовым ответом'},
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 2 опроса 5 с текстовым ответом'},
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 3 опроса 5 с текстовым ответом'},
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 4 опроса 5 с текстовым ответом'},
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 5 опроса 5 с текстовым ответом'},
        {'poll_id': pol[4],
         'question_type': TEXT,
         'question_text': 'Вопрос 6 опроса 5 с текстовым ответом'},
    ]

    for item in questions:
        Question.objects.create(**item)
    # Опрос 1: один - 4-6, несколько 7-9
    # Опрос 2: один - 13-15, несколько 16-18
    # Опрос 3: один - 22-24, несколько 25-27

    q = Question.objects.all()

    question_options = [
        {'question_id': q[3],
         'question_answer': 'Ответ 1 на вопрос 4 опроса 1'},
        {'question_id': q[3],
         'question_answer': 'Ответ 2 на вопрос 4 опроса 1'},
        {'question_id': q[3],
         'question_answer': 'Ответ 3 на вопрос 4 опроса 1'},
        {'question_id': q[3],
         'question_answer': 'Ответ 4 на вопрос 4 опроса 1'},
        {'question_id': q[4],
         'question_answer': 'Ответ 1 на вопрос 5 опроса 1'},
        {'question_id': q[4],
         'question_answer': 'Ответ 2 на вопрос 5 опроса 1'},
        {'question_id': q[4],
         'question_answer': 'Ответ 3 на вопрос 5 опроса 1'},
        {'question_id': q[5],
         'question_answer': 'Ответ 1 на вопрос 6 опроса 1'},
        {'question_id': q[5],
         'question_answer': 'Ответ 2 на вопрос 6 опроса 1'},
        {'question_id': q[5],
         'question_answer': 'Ответ 3 на вопрос 6 опроса 1'},
        {'question_id': q[6],
         'question_answer': 'Ответ 1 на вопрос 7 опроса 1'},
        {'question_id': q[6],
         'question_answer': 'Ответ 2 на вопрос 7 опроса 1'},
        {'question_id': q[6],
         'question_answer': 'Ответ 3 на вопрос 7 опроса 1'},
        {'question_id': q[6],
         'question_answer': 'Ответ 4 на вопрос 7 опроса 1'},
        {'question_id': q[7],
         'question_answer': 'Ответ 1 на вопрос 8 опроса 1'},
        {'question_id': q[7],
         'question_answer': 'Ответ 2 на вопрос 8 опроса 1'},
        {'question_id': q[7],
         'question_answer': 'Ответ 3 на вопрос 8 опроса 1'},
        {'question_id': q[7],
         'question_answer': 'Ответ 4 на вопрос 8 опроса 1'},
        {'question_id': q[7],
         'question_answer': 'Ответ 5 на вопрос 8 опроса 1'},
        {'question_id': q[8],
         'question_answer': 'Ответ 1 на вопрос 9 опроса 1'},
        {'question_id': q[8],
         'question_answer': 'Ответ 2 на вопрос 9 опроса 1'},
        {'question_id': q[8],
         'question_answer': 'Ответ 3 на вопрос 9 опроса 1'},
        {'question_id': q[8],
         'question_answer': 'Ответ 4 на вопрос 9 опроса 1'},
        {'question_id': q[8],
         'question_answer': 'Ответ 5 на вопрос 9 опроса 1'},
        # опрос 2
        {'question_id': q[12],
         'question_answer': 'Ответ 1 на вопрос 4 опроса 2'},
        {'question_id': q[12],
         'question_answer': 'Ответ 2 на вопрос 4 опроса 2'},
        {'question_id': q[12],
         'question_answer': 'Ответ 3 на вопрос 4 опроса 2'},
        {'question_id': q[12],
         'question_answer': 'Ответ 4 на вопрос 4 опроса 2'},
        {'question_id': q[13],
         'question_answer': 'Ответ 1 на вопрос 5 опроса 2'},
        {'question_id': q[13],
         'question_answer': 'Ответ 2 на вопрос 5 опроса 2'},
        {'question_id': q[13],
         'question_answer': 'Ответ 3 на вопрос 5 опроса 2'},
        {'question_id': q[14],
         'question_answer': 'Ответ 1 на вопрос 6 опроса 2'},
        {'question_id': q[14],
         'question_answer': 'Ответ 2 на вопрос 6 опроса 2'},
        {'question_id': q[14],
         'question_answer': 'Ответ 3 на вопрос 6 опроса 2'},
        {'question_id': q[15],
         'question_answer': 'Ответ 1 на вопрос 7 опроса 2'},
        {'question_id': q[15],
         'question_answer': 'Ответ 2 на вопрос 7 опроса 2'},
        {'question_id': q[15],
         'question_answer': 'Ответ 3 на вопрос 7 опроса 2'},
        {'question_id': q[15],
         'question_answer': 'Ответ 4 на вопрос 7 опроса 2'},
        {'question_id': q[16],
         'question_answer': 'Ответ 1 на вопрос 8 опроса 2'},
        {'question_id': q[16],
         'question_answer': 'Ответ 2 на вопрос 8 опроса 2'},
        {'question_id': q[16],
         'question_answer': 'Ответ 3 на вопрос 8 опроса 2'},
        {'question_id': q[16],
         'question_answer': 'Ответ 4 на вопрос 8 опроса 2'},
        {'question_id': q[16],
         'question_answer': 'Ответ 5 на вопрос 8 опроса 2'},
        {'question_id': q[17],
         'question_answer': 'Ответ 1 на вопрос 9 опроса 2'},
        {'question_id': q[17],
         'question_answer': 'Ответ 2 на вопрос 9 опроса 2'},
        {'question_id': q[17],
         'question_answer': 'Ответ 3 на вопрос 9 опроса 2'},
        {'question_id': q[17],
         'question_answer': 'Ответ 4 на вопрос 9 опроса 2'},
        {'question_id': q[17],
         'question_answer': 'Ответ 5 на вопрос 9 опроса 2'},
        # опрос 3
        {'question_id': q[21],
         'question_answer': 'Ответ 1 на вопрос 4 опроса 3'},
        {'question_id': q[21],
         'question_answer': 'Ответ 2 на вопрос 4 опроса 3'},
        {'question_id': q[21],
         'question_answer': 'Ответ 3 на вопрос 4 опроса 3'},
        {'question_id': q[21],
         'question_answer': 'Ответ 4 на вопрос 4 опроса 3'},
        {'question_id': q[22],
         'question_answer': 'Ответ 1 на вопрос 5 опроса 3'},
        {'question_id': q[22],
         'question_answer': 'Ответ 2 на вопрос 5 опроса 3'},
        {'question_id': q[22],
         'question_answer': 'Ответ 3 на вопрос 5 опроса 3'},
        {'question_id': q[23],
         'question_answer': 'Ответ 1 на вопрос 6 опроса 3'},
        {'question_id': q[23],
         'question_answer': 'Ответ 2 на вопрос 6 опроса 3'},
        {'question_id': q[23],
         'question_answer': 'Ответ 3 на вопрос 6 опроса 3'},
        {'question_id': q[24],
         'question_answer': 'Ответ 1 на вопрос 7 опроса 3'},
        {'question_id': q[24],
         'question_answer': 'Ответ 2 на вопрос 7 опроса 3'},
        {'question_id': q[24],
         'question_answer': 'Ответ 3 на вопрос 7 опроса 3'},
        {'question_id': q[24],
         'question_answer': 'Ответ 4 на вопрос 7 опроса 3'},
        {'question_id': q[25],
         'question_answer': 'Ответ 1 на вопрос 8 опроса 3'},
        {'question_id': q[25],
         'question_answer': 'Ответ 2 на вопрос 8 опроса 3'},
        {'question_id': q[25],
         'question_answer': 'Ответ 3 на вопрос 8 опроса 3'},
        {'question_id': q[25],
         'question_answer': 'Ответ 4 на вопрос 8 опроса 3'},
        {'question_id': q[25],
         'question_answer': 'Ответ 5 на вопрос 8 опроса 3'},
        {'question_id': q[26],
         'question_answer': 'Ответ 1 на вопрос 9 опроса 3'},
        {'question_id': q[26],
         'question_answer': 'Ответ 2 на вопрос 9 опроса 3'},
        {'question_id': q[26],
         'question_answer': 'Ответ 3 на вопрос 9 опроса 3'},
        {'question_id': q[26],
         'question_answer': 'Ответ 4 на вопрос 9 опроса 3'},
        {'question_id': q[26],
         'question_answer': 'Ответ 5 на вопрос 9 опроса 3'}
    ]

    for item in question_options:
        QuestionOptions.objects.create(**item)

    qp = QuestionOptions.objects.all()
    users = User.objects.all()

    user_answers = [
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[0],
         'user_answer': 'Текстовый ответ 1 на вопрос 1 опроса 1'},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[1],
         'user_answer': 'Текстовый ответ 2 на вопрос 2 опроса 1'},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[2],
         'user_answer': 'Текстовый ответ 3 на вопрос 3 опроса 1'},

        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[3],
         'question_option_id': qp[0]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[4],
         'question_option_id': qp[6]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[5],
         'question_option_id': qp[9]},

        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[6],
         'question_option_id': qp[10]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[6],
         'question_option_id': qp[11]},

        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[7],
         'question_option_id': qp[16]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[7],
         'question_option_id': qp[18]},

        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[8],
         'question_option_id': qp[19]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[8],
         'question_option_id': qp[20]},
        {'user_id': users[0],
         'poll_id': pol[0],
         'question_id': q[8],
         'question_option_id': qp[21]},

        {'user_id': users[0],
         'poll_id': pol[4],
         'question_id': q[27],
         'user_answer': 'Текстовый ответ 1 на вопрос 1 опроса 5'},
        {'user_id': users[0],
         'poll_id': pol[4],
         'question_id': q[28],
         'user_answer': 'Текстовый ответ 2 на вопрос 2 опроса 5'},
        {'user_id': users[0],
         'poll_id': pol[4],
         'question_id': q[28],
         'user_answer': 'Текстовый ответ 3 на вопрос 3 опроса 5'},

        # {'user_id': users[1],
        #  'poll_id': pol[4],
        #  'question_id': q[29],
        #  'user_answer': 'Текстовый ответ 1 на вопрос 1 опроса 5'},
        # {'user_id': users[1],
        #  'poll_id': pol[4],
        #  'question_id': q[30],
        #  'user_answer': 'Текстовый ответ 2 на вопрос 2 опроса 5'},
        # {'user_id': users[1],
        #  'poll_id': pol[4],
        #  'question_id': q[31],
        #  'user_answer': 'Текстовый ответ 3 на вопрос 3 опроса 5'},
    ]
    for item in user_answers:
        UsersAnswers.objects.create(**item)
