from api.models import User
from django.db import models


class Poll(models.Model):
    """Модель опроса"""
    name = models.CharField(verbose_name='Название опроса', max_length=200, blank=False)
    description = models.TextField(verbose_name='Описание опроса', blank=False)
    start_date = models.DateField(verbose_name='Старт опроса', blank=False)
    end_date = models.DateField(verbose_name='Окончание опроса', blank=False)
    is_active = models.BooleanField(verbose_name='Активность', blank=False, default=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    """Модель вопроса"""
    TEXT = 'TEXT_ANSWER'
    ONE_ANSWER = 'ONE_ANSWER'
    MANY_ANSWERS = 'MANY_ANSWERS'
    QST_TYPES = (
        (TEXT, 'Текстовый ответ'),
        (ONE_ANSWER, 'Один ответ'),
        (MANY_ANSWERS, 'Несколько ответов'),
    )
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='Опрос',
                                null=True, blank=True)
    question_type = models.CharField(verbose_name='Тип вопроса', max_length=12, choices=QST_TYPES, default=TEXT)
    question_text = models.TextField(verbose_name='Вопрос', blank=False)
    is_active = models.BooleanField(verbose_name='Активность', default=True, blank=False)

    def __str__(self):
        return self.question_text


class QuestionOptions(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос', blank=False)
    question_answer = models.CharField(verbose_name='Ответ на вопрос', max_length=4000, blank=False)
    is_active = models.BooleanField(verbose_name='Активность', blank=False, default=True)

    def __str__(self):
        return f'{self.question_answer}'


class UsersAnswers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=False)
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='Опрос', blank=False)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос', blank=False)
    question_option_id = models.ForeignKey(QuestionOptions, on_delete=models.CASCADE, verbose_name='Вариант ответа',
                                           blank=True, null=True)
    user_answer = models.CharField(verbose_name='Текстовый ответ пользователя', max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.user_id} {self.poll_id}'

    # class Meta:
    #     constraints = [models.UniqueConstraint(fields=['poll_id', 'question_id', 'question_option_id'],
    #                                            name='unique_UsersAnswers_poll_id_question_id_question_option_id')]
