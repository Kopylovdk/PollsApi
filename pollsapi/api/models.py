import jwt
from django.contrib.auth.models import AbstractUser
from django.db import models
from main import settings


class User(AbstractUser):
    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор пользователя
        """
        token = jwt.encode({'id': self.pk}, settings.SECRET_KEY, algorithm='HS256')
        return token

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Poll(models.Model):
    """Модель опроса"""
    name = models.CharField(verbose_name='Название опроса', max_length=200, blank=False)
    description = models.TextField(verbose_name='Описание опроса', blank=False)
    start_date = models.DateField(verbose_name='Старт опроса', blank=False)
    end_date = models.DateField(verbose_name='Окончание опроса', blank=False)
    is_active = models.BooleanField(verbose_name='Активность', blank=False, default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'опрос'
        verbose_name_plural = 'опросы'


class Question(models.Model):
    """Модель вопроса"""
    TEXT = 'TEXT_ANSWER'
    CHOSE_ANSWER = 'CHOSE_ANSWER'
    QST_TYPES = (
        (TEXT, 'Текстовый ответ'),
        (CHOSE_ANSWER, 'Варианты ответов'),
    )
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='Опрос', blank=False)
    question_type = models.CharField(verbose_name='Тип вопроса', max_length=12, choices=QST_TYPES, default=TEXT)
    question_text = models.TextField(verbose_name='Вопрос', blank=False)
    is_active = models.BooleanField(verbose_name='Активность', default=True, blank=False)

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class QuestionOptions(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос', blank=False)
    question_answer = models.CharField(verbose_name='Ответ на вопрос', max_length=4000, blank=False)
    is_active = models.BooleanField(verbose_name='Активность', blank=False, default=True)

    def __str__(self):
        return f'{self.question_answer}'

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответов'


class UsersAnswers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=False)
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='Опрос', blank=False)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос', blank=False)
    question_option_id = models.ForeignKey(QuestionOptions, on_delete=models.CASCADE, verbose_name='Вариант ответа',
                                           blank=True, null=True)
    user_answer = models.CharField(verbose_name='Текстовый ответ пользователя', max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.user_id} {self.poll_id}'

    class Meta:
        verbose_name = 'ответы пользователя'
        verbose_name_plural = 'ответы пользователей'
