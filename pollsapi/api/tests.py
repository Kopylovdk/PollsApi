import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import User, Poll, Question, QuestionOptions, UsersAnswers
from api.data_for_tests import data_add_to_tst_db


class UserCreateTest(APITestCase):
    def setUp(self):
        self.data = {'user': {
            'username': 'test',
            'password': '123456',
            "email": 'test@test.ru'
        }}

    def test_create_user(self):
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

    def test_auth_user(self):
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

    def test_get_user_data(self):
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

    def test_update_user(self):
        result = self.client.patch(reverse('api:data'), self.data_update, HTTP_AUTHORIZATION=self.headers,
                                   format='json')
        self.correct_data['user']['first_name'] = User.objects.get(username='test').first_name
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(self.correct_data, result.json())


class PollsCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('api:poll')
        self.user_token = f"Token {User.objects.create_user(username='test', email='test@test.ru', password='123456').token}"
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.new_poll_data = {"polls": {"name": "test",
                                        "description": "test",
                                        "start_date": datetime.date.today(),
                                        "end_date": datetime.date.today() + datetime.timedelta(days=2)
                                        }
                              }

    def test_create_poll_superuser(self):
        result = self.client.post(self.url, self.new_poll_data, HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in result.json()['polls'])

    def test_create_poll_user(self):
        result = self.client.post(self.url, self.new_poll_data, HTTP_AUTHORIZATION=self.user_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())


class PollsReadTest(APITestCase):
    def setUp(self):
        self.user_token = f"Token {User.objects.create_user(username='test', email='test@test.ru', password='123456').token}"
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        data_add_to_tst_db()
        self.new_poll_data = {"polls": {"name": "test",
                                        "description": "test",
                                        "start_date": datetime.date.today(),
                                        "end_date": datetime.date.today() + datetime.timedelta(days=2)
                                        }
                              }
        self.url = reverse('api:poll')

    def test_get_one_poll(self):
        result = self.client.get(reverse('api:poll_pk', kwargs={'pk': Poll.objects.all()[0].id}),
                                 HTTP_AUTHORIZATION=self.user_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('poll' in result.json())
        self.assertTrue('questions' in result.json())
        self.assertTrue('question_options' in result.json()['questions'][0])

    def test_get_all_polls(self):
        result = self.client.get(self.url, HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in result.json()['polls'][0])
        self.assertEqual(len(Poll.objects.all()), len(result.json()['polls']))

    def test_get_all_active_polls(self):
        result = self.client.get(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in result.json()['polls'][0])
        self.assertEqual(len(Poll.objects.filter(is_active=True)), len(result.json()['polls']))


class PollUpdateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.anonymous_token = f"Token {User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru', password='123456').token}"
        self.poll_data = {'name': 'Опрос номер 1',
                          'description': 'Описание опроса номер 1',
                          'start_date': datetime.date.today(),
                          'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.url = reverse('api:poll_pk', kwargs={'pk': Poll.objects.create(**self.poll_data).id})
        self.poll_data_update = {"polls": {"description": "test update"}}

    def test_update_poll_no_data(self):
        result = self.client.patch(self.url, HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_update_poll_bad_pk(self):
        result = self.client.patch(reverse('api:poll_pk', kwargs={'pk': 10000}), self.poll_data_update,
                                   HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_update_poll_user(self):
        result = self.client.patch(self.url, self.poll_data_update,
                                   HTTP_AUTHORIZATION=self.anonymous_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_update_poll_superuser(self):
        result = self.client.patch(self.url, self.poll_data_update, HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(Poll.objects.get(id=result.json()['polls']['id']).description,
                         result.json()['polls']['description'])


class PollDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.anonymous_token = f"Token {User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru', password='123456').token}"
        self.poll_data = {'name': 'Опрос номер 1',
                          'description': 'Описание опроса номер 1',
                          'start_date': datetime.date.today(),
                          'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.url = reverse('api:poll_pk', kwargs={'pk': Poll.objects.create(**self.poll_data).id})

    def test_delete_poll_bad_data(self):
        result = self.client.delete(self.url, {"eggs": {"eggs": "eggs"}},
                                    HTTP_AUTHORIZATION=self.admin_token, format='json')
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_delete_poll_no_auth(self):
        result = self.client.delete(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())
        result = self.client.delete(self.url, format='json', HTTP_AUTHORIZATION=self.anonymous_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_delete_poll_bad_pk(self):
        result = self.client.delete(reverse('api:poll_pk', kwargs={'pk': 10000}),
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)

    def test_poll_superuser_delete(self):
        result = self.client.delete(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('detail' in result.json())
        self.assertFalse(Poll.objects.get(name='Опрос номер 1').is_active)


class QuestionCreateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.p_data = {"name": "test",
                       "description": "test",
                       "start_date": datetime.date.today(),
                       "end_date": datetime.date.today() + datetime.timedelta(days=2)
                       }
        self.q_data = {"question": {"question_type": 'CHOSE_ANSWER',
                                    "question_text": "Тестовое создание"
                                    },
                       'question_options': ['test 1', 'test 2', 'test 3']
                       }
        self.url = reverse('api:question', kwargs={'pk': Poll.objects.create(**self.p_data).id})

    def test_create_question_no_auth(self):
        result = self.client.post(self.url, self.q_data, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_create_question_bad_poll_id(self):
        result = self.client.post(reverse('api:question', kwargs={'pk': 10000}), self.q_data, format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_question_poll_deactivate(self):
        self.p_data['is_active'] = False
        result = self.client.post(reverse('api:question',
                                          kwargs={'pk': Poll.objects.create(**self.p_data).id}),
                                  self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_create_question_no_data(self):
        result = self.client.post(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_bad_data_no_question_option(self):
        del (self.q_data['question_options'])
        result = self.client.post(self.url, self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_bad_q_type(self):
        self.q_data["question"]["question_type"] = 'eggs'
        result = self.client.post(self.url, self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())
        self.assertTrue('question_type' in result.json()['errors'])

    def test_create_question_text_answer(self):
        self.q_data["question"]["question_type"] = 'TEXT_ANSWER'
        del (self.q_data['question_options'])
        result = self.client.post(self.url, self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
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
        result = self.client.post(self.url, self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
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


class QuestionUpdateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.p_data = {"name": "test",
                       "description": "test",
                       "start_date": datetime.date.today(),
                       "end_date": datetime.date.today() + datetime.timedelta(days=2)
                       }
        self.p = Poll.objects.create(**self.p_data)
        self.q_data = {"question": {"question_type": 'CHOSE_ANSWER',
                                    "question_text": "Тестовое создание",
                                    "poll_id": self.p
                                    },
                       'question_options': ['test 1', 'test 2', 'test 3']
                       }
        self.q = Question.objects.create(**self.q_data['question'])
        self.q_data["question"]["poll_id"] = self.p.id
        self.url = reverse('api:question', kwargs={'pk': self.q.id})
        self.update_data = 'data after update'

    def test_update_question_no_auth(self):
        self.q_data['question']["question_text"] = self.update_data
        result = self.client.patch(self.url, self.q_data, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_update_question_no_data(self):
        result = self.client.patch(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_update_question_bad_pk(self):
        self.q_data['question']["question_text"] = self.update_data
        result = self.client.patch(reverse('api:question', kwargs={'pk': 10000}), self.q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_update_question_chose_answer_poll_inactive(self):
        self.p_data['is_active'] = False
        self.q_data['question']["poll_id"] = Poll.objects.create(**self.p_data).id
        result = self.client.patch(self.url, self.q_data,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_update_question_chose_answer(self):
        self.q_data['question']["question_text"] = self.update_data
        result = self.client.patch(self.url, self.q_data, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('question' in result.json())
        check = Question.objects.get(id=self.q.id)
        self.assertEqual(check.question_type, 'CHOSE_ANSWER')
        self.assertEqual(check.question_text, self.update_data)
        self.assertEqual(check.id, result.json()['question']['id'])

    # На мой взгляд - это избыточно, есть test_update_question_chose_answer и отличаются они только question_type
    # def test_update_question_text_answer(self):
    #     self.q_data['question']['question_type'] = 'TEXT_ANSWER'
    #     self.q_data["question"]["poll_id"] = self.p
    #     q_text = Question.objects.create(**self.q_data['question'])
    #     self.q_data['question']["question_text"] = self.update_data
    #     self.q_data["question"]["poll_id"] = self.p.id
    #     result = self.client.patch(reverse('api:question', kwargs={'pk': q_text.id}), self.q_data,
    #                                format='json', HTTP_AUTHORIZATION=self.admin_token)
    #     self.assertEqual(result.status_code, status.HTTP_200_OK)
    #     self.assertTrue('question' in result.json())
    #     check = Question.objects.get(id=q_text.id)
    #     self.assertEqual(check.question_type, 'TEXT_ANSWER')
    #     self.assertEqual(check.question_text, self.update_data)
    #     self.assertEqual(check.id, result.json()['question']['id'])


class QuestionDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.p_data = {"name": "test",
                       "description": "test",
                       "start_date": datetime.date.today(),
                       "end_date": datetime.date.today() + datetime.timedelta(days=2)
                       }
        self.q_data = {"question": {"question_type": 'CHOSE_ANSWER',
                                    "question_text": "Тестовое создание",
                                    "poll_id": Poll.objects.create(**self.p_data)
                                    },
                       'question_options': ['test 1', 'test 2', 'test 3']
                       }
        self.url = reverse('api:question', kwargs={'pk': Question.objects.create(**self.q_data['question']).id})

    def test_delete_question_no_auth(self):
        result = self.client.delete(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_delete_question_with_data(self):
        result = self.client.delete(self.url, {"eggs": {"eggs": "eggs"}}, format='json',
                                    HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_delete_question_bad_pk(self):
        result = self.client.delete(reverse('api:question', kwargs={'pk': 100000}),
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_delete_question(self):
        result = self.client.delete(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('detail' in result.json())


class QuestionOptionsCreateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.qo_to_create = {"question_options": [{"question_answer": "Тестовое добавление варианта ответа 10"},
                                                  {"question_answer": "Тестовое добавление варианта ответа 11"}]
                             }
        self.p_data = {'name': 'Опрос номер 1',
                       'description': 'Описание опроса номер 1',
                       'start_date': datetime.date.today(),
                       'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.to_create_q = {'poll_id': Poll.objects.create(**self.p_data),
                            'question_type': 'CHOSE_ANSWER',
                            'question_text': 'Тест',
                            }
        self.url = reverse('api:question_options', kwargs={'pk': Question.objects.create(**self.to_create_q).id})

    def test_create_question_options_no_auth(self):
        result = self.client.post(self.url, self.qo_to_create, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_create_question_options_bad_question_id(self):
        result = self.client.post(reverse('api:question_options', kwargs={'pk': 10000}), self.qo_to_create,
                                  format='json',
                                  HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_question_options_inactive_question(self):
        self.to_create_q['is_active'] = False
        result = self.client.post(reverse('api:question_options',
                                          kwargs={'pk': Question.objects.create(**self.to_create_q).id}),
                                  self.qo_to_create, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_create_question_options_no_data(self):
        result = self.client.post(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_question_options(self):
        result = self.client.post(self.url, self.qo_to_create,
                                  format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertTrue('question_options' in result.json())
        self.assertTrue('id' in result.json()['question_options'][0])


class QuestionOptionsUpdateTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.data_to_update = {"question_options": {"question_answer": "Тестовое изменение варианта ответа"}}
        self.p_data = {'name': 'Опрос номер 1',
                       'description': 'Описание опроса номер 1',
                       'start_date': datetime.date.today(),
                       'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.to_create_q = {'poll_id': Poll.objects.create(**self.p_data),
                            'question_type': 'CHOSE_ANSWER',
                            'question_text': 'Тест',
                            }
        self.to_create_qo = {'question_id': Question.objects.create(**self.to_create_q),
                             'question_answer': 'test',
                             }
        self.url = reverse('api:question_options',
                           kwargs={'pk': QuestionOptions.objects.create(**self.to_create_qo).id})

    def test_update_question_options_no_auth(self):
        result = self.client.patch(self.url, self.data_to_update, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_update_question_options_bad_question_option_id(self):
        result = self.client.patch(reverse('api:question_options', kwargs={'pk': 10000}), self.data_to_update,
                                   format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_update_question_options_bad_question_id(self):
        self.data_to_update['question_options']['question_id'] = 100000
        result = self.client.patch(self.url, self.data_to_update, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_update_question_options_no_data(self):
        result = self.client.patch(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_update_question_options_inactive_question_option(self):
        self.to_create_qo['is_active'] = False
        qo_inactive_id = QuestionOptions.objects.create(**self.to_create_qo).id
        result = self.client.patch(reverse('api:question_options', kwargs={'pk': qo_inactive_id}),
                                   self.data_to_update, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_update_question_options_inactive_question(self):
        self.to_create_q['is_active'] = False
        q_inactive_id = Question.objects.create(**self.to_create_q).id
        self.data_to_update['question_options']['question_id'] = q_inactive_id
        result = self.client.patch(self.url, self.data_to_update, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('errors' in result.json())

    def test_update_question_options(self):
        result = self.client.patch(self.url, self.data_to_update, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('question_options' in result.json())
        qo = QuestionOptions.objects.get(id=result.json()['question_options']['id'])
        correct_data = {'question_options': {'id': qo.id, 'question_answer': qo.question_answer,
                                             'is_active': qo.is_active, 'question_id': qo.question_id.id}}
        self.assertEqual(correct_data, result.json())


class QuestionOptionsDeleteTest(APITestCase):
    def setUp(self):
        self.admin_token = f"Token {User.objects.create_superuser(username='admin', email='admin@admin.ru', password='123456').token}"
        self.p_data = {'name': 'Опрос номер 1',
                       'description': 'Описание опроса номер 1',
                       'start_date': datetime.date.today(),
                       'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.to_create_q = {'poll_id': Poll.objects.create(**self.p_data),
                            'question_type': 'CHOSE_ANSWER',
                            'question_text': 'Тест',
                            }
        self.to_create_qo = {'question_id': Question.objects.create(**self.to_create_q),
                             'question_answer': 'test',
                             }
        self.url = reverse('api:question_options',
                           kwargs={'pk': QuestionOptions.objects.create(**self.to_create_qo).id})

    def test_delete_question_options_no_auth(self):
        result = self.client.delete(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in result.json())

    def test_delete_question_options_with_data(self):
        result = self.client.delete(self.url, {"eggs": {"eggs": "eggs"}},
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('errors' in result.json())

    def test_delete_question_options_bad_pk(self):
        result = self.client.delete(reverse('api:question_options', kwargs={'pk': 100000}),
                                    format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_delete_question(self):
        result = self.client.delete(self.url, format='json', HTTP_AUTHORIZATION=self.admin_token)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('detail' in result.json())


class UserAnswersReadTest(APITestCase):
    def setUp(self):
        self.user_token = f"Token {User.objects.create_user(username='test', email='test@test.ru', password='123456').token}"
        data_add_to_tst_db()
        self.url = reverse('api:user_polls_get')

    def test_user_answers_get_answers_no_auth(self):
        result = self.client.get(self.url, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_user_answers_get_answers(self):
        result = self.client.get(self.url, format='json', HTTP_AUTHORIZATION=self.user_token)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertTrue('polls' in result.json())
        self.assertTrue(isinstance(result.json()['polls'], list))
        self.assertEqual(len(result.json()['polls']), 3)


class UserAnswersCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.ru', password='123456')
        self.user_token = f"Token {self.user.token}"
        self.anonymous = User.objects.create_user(username='anonymous', email='anonymous@anonymous.ru',
                                                  password='123456')
        self.p_data = {'name': 'Опрос номер 1',
                       'description': 'Описание опроса номер 1',
                       'start_date': datetime.date.today(),
                       'end_date': datetime.date.today() + datetime.timedelta(days=2)}
        self.p = Poll.objects.create(**self.p_data)
        self.to_create_q_chose = {'poll_id': self.p,
                                  'question_type': 'CHOSE_ANSWER',
                                  'question_text': 'Тест',
                                  }
        self.q_chose = Question.objects.create(**self.to_create_q_chose)
        self.to_create_qo_1 = {'question_id': self.q_chose,
                               'question_answer': 'test 1',
                               }
        self.to_create_qo_2 = {'question_id': self.q_chose,
                               'question_answer': 'test 2',
                               }
        self.to_create_qo_3 = {'question_id': self.q_chose,
                               'question_answer': 'test 2',
                               }
        self.qo_1 = QuestionOptions.objects.create(**self.to_create_qo_1)
        self.qo_2 = QuestionOptions.objects.create(**self.to_create_qo_2)
        self.qo_3 = QuestionOptions.objects.create(**self.to_create_qo_3)
        self.to_create_q_text = {'poll_id': self.p,
                                 'question_type': 'TEXT_ANSWER',
                                 'question_text': 'Тест',
                                 }
        self.q_text = Question.objects.create(**self.to_create_q_text)
        self.url = 'api:user_question_answer'
        self.answer = {"answers": {"question_option_id": [self.qo_1.id, self.qo_2.id], "user_answer": "eggs and span"}}

    def test_create_user_answers_no_answer_data(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_text.id}), {'eggs': 'eggs'},
                                  format='json', HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_user_answers_bad_pk(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': 100000}), self.answer,
                                  format='json', HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_user_answers_no_question_option_id_in_data(self):
        del self.answer['answers']['question_option_id']
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_chose.id}), self.answer,
                                  format='json', HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_user_answers_bad_question_option_id_in_data(self):
        self.answer['answers']['question_option_id'] = [1, 333]
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_chose.id}), self.answer,
                                  format='json', HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in result.json())

    def test_create_user_answers_auth_chose(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_chose.id}), self.answer,
                                  format='json', HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'answers': 'Data saved'}, result.json())
        self.assertEqual(len(UsersAnswers.objects.filter(user_id=self.user.id)), 2)

    def test_create_user_answers_no_auth_chose(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_chose.id}), self.answer, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'answers': 'Data saved'}, result.json())
        self.assertEqual(len(UsersAnswers.objects.filter(user_id=self.anonymous.id)), 2)

    def test_create_user_answers_no_user_answer_data(self):
        del self.answer['answers']['user_answer']
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_text.id}), self.answer, format='json')
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('errors' in result.json())

    def test_create_user_answers_no_auth_text(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_text.id}), self.answer, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'answers': 'Data saved'}, result.json())
        self.assertEqual(len(UsersAnswers.objects.filter(user_id=self.anonymous.id)), 1)

    def test_create_user_answers_auth_text(self):
        result = self.client.post(reverse(self.url, kwargs={'pk': self.q_text.id}), self.answer, format='json',
                                  HTTP_AUTHORIZATION=self.user_token)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'answers': 'Data saved'}, result.json())
        self.assertEqual(len(UsersAnswers.objects.filter(user_id=self.user.id)), 1)
