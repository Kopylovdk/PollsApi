import datetime
from api.models import User, Poll, Question, QuestionOptions, UsersAnswers


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
         'poll_id': pol[1],
         'question_id': q[7],
         'user_answer': 'Текстовый ответ 1 на вопрос 7 опроса 2'},
        {'user_id': users[0],
         'poll_id': pol[2],
         'question_id': q[12],
         'question_option_id': qp[11]},
        {'user_id': users[0],
         'poll_id': pol[2],
         'question_id': q[12],
         'question_option_id': qp[12]},
    ]
    for item in user_answers:
        UsersAnswers.objects.create(**item)
