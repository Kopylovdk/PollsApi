from rest_framework import status
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import User
from api.serializers import LoginSerializer, PollsSerializer, RegistrationSerializer, UserSerializer, \
    QuestionSerializer, UserAnswerSerializer, QuestionOptionsSerializer
from api.renderers import UserJSONRenderer, ClassJSONRenderer
from polls.models import Poll, Question, QuestionOptions, UsersAnswers


class UserLoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PollsActiveListAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PollsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def get(self, request):
        polls = Poll.objects.filter(is_active=True)
        serializer = self.serializer_class(polls, many=True)
        return Response({'polls': serializer.data}, status=status.HTTP_200_OK)


class PollsOneAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PollsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def get(self, request, pk):
        poll = Poll.objects.filter(id=pk, is_active=True).first()
        if not poll:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer_poll = self.serializer_class(poll)
        dict_to_return = {
            'poll': serializer_poll.data,
            'questions': []
        }
        for q in Question.objects.filter(poll_id=pk, is_active=True):
            serializer_questions = QuestionSerializer(q)
            to_insert = {'question': serializer_questions.data,
                         'question_options': []}
            for qo in QuestionOptions.objects.filter(question_id=q.id, is_active=True):
                serializer_qo = QuestionOptionsSerializer(qo)
                to_insert['question_options'].append(serializer_qo.data)
            dict_to_return['questions'].append(to_insert)
        return Response(dict_to_return, status=status.HTTP_200_OK)


class PollsAPIView(APIView):
    permission_classes = (IsAdminUser,)
    serializer_class = PollsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def get(self, request):
        polls = Poll.objects.all()
        serializer = self.serializer_class(polls, many=True)
        return Response({'polls': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        poll = request.data.get('polls')
        serializer = self.serializer_class(data=poll)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'polls': serializer.data}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        new_poll = request.data.get('polls')
        poll = get_object_or_404(Poll, id=pk)
        active_change_flag = None
        keys = new_poll.keys()
        if 'is_active' in keys and poll.is_active != new_poll['is_active']:
            active_change_flag = new_poll['is_active']
        if 'start_date' in keys:
            del (new_poll['start_date'])
        serializer = self.serializer_class(instance=poll, data=new_poll, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if active_change_flag is not None:
            q_deactivation(active_change_flag, poll.id)
        return Response(serializer.data, status.HTTP_200_OK)


class QuestionAPIView(APIView):
    permission_classes = (IsAdminUser,)
    serializer_class = QuestionSerializer
    renderer_classes = (ClassJSONRenderer,)

    def post(self, request):
        question = request.data.get('question')
        question_options = request.data.get('question_options')
        if question['question_type'] in ['MANY_ANSWERS', 'ONE_ANSWER'] and not question_options:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(data=question)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        to_send = {'question': serializer.data}
        if question['question_type'] in ['MANY_ANSWERS', 'ONE_ANSWER'] and question_options:
            to_send['question_options'] = []
            for qo in question_options:
                qo_to_create = {'question_answer': qo,
                                'question_id': serializer.data.get('id')}
                serializer_qo = QuestionOptionsSerializer(data=qo_to_create)
                serializer_qo.is_valid(raise_exception=True)
                serializer_qo.save()
                to_send['question_options'].append(serializer_qo.data)
            return Response(to_send, status=status.HTTP_201_CREATED)
        else:
            return Response(to_send, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        new_question = request.data.get('question')
        question = get_object_or_404(Question, id=pk)
        active_chang_flag = None
        if 'is_active' in new_question.keys() and question.is_active != new_question['is_active']:
            active_chang_flag = new_question['is_active']
        serializer = self.serializer_class(instance=question, data=new_question, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if active_chang_flag is not None and serializer.data.get('question_type') in ['MANY_ANSWERS', 'ONE_ANSWER']:
            qo_deactivation(serializer.data.get('is_active'), serializer.data.get('id'))
        return Response(serializer.data, status.HTTP_200_OK)


def q_deactivation(choice, p_id):
    if choice:
        for q in Question.objects.filter(poll_id=p_id):
            q.is_active = True
            q.save()
            if q.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
                qo_deactivation(q.is_active, q.id)
    else:
        for q in Question.objects.filter(poll_id=p_id):
            q.is_active = False
            q.save()
            if q.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
                qo_deactivation(q.is_active, q.id)


def qo_deactivation(choice, q_id):
    if choice:
        for qo in QuestionOptions.objects.filter(question_id=q_id):
            qo.is_active = True
            qo.save()
    else:
        for qo in QuestionOptions.objects.filter(question_id=q_id):
            qo.is_active = False
            qo.save()


class QuestionOptionsAPIView(APIView):
    permission_classes = (IsAdminUser,)
    serializer_class = QuestionOptionsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def post(self, request):
        question_options = request.data.get('question_options')
        qo = {'question_options': []}
        for q_o in question_options:
            serializer = self.serializer_class(data=q_o)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            qo['question_options'].append(serializer.data)
        return Response(qo, status=status.HTTP_201_CREATED)

    def patch(self, request):
        new_qo = request.data.get('question_options')
        qo = {'question_options': []}
        for nqo in new_qo:
            q_o = get_object_or_404(QuestionOptions, id=nqo['id'])
            serializer = self.serializer_class(instance=q_o, data=nqo, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            qo['question_options'].append(serializer.data)
        return Response(qo, status.HTTP_200_OK)


class UserAnswersAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserAnswerSerializer
    renderer_classes = (ClassJSONRenderer,)

    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            dict_with_polls = {'polls': []}
            ua = UsersAnswers.objects.filter(user_id=user_id)
            q = Question.objects.all()
            qo = QuestionOptions.objects.all()
            for u_p in ua.values_list('poll_id').distinct():
                p = Poll.objects.filter(id=u_p[0]).first()
                p_serializer = PollsSerializer(p)
                data = {'poll': p_serializer.data,
                        'questions': []}
                for quest in q.filter(poll_id=p.id):
                    q_serializer = QuestionSerializer(quest)
                    to_data = {'question': q_serializer.data,
                               'answers': []}
                    if quest.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
                        span = ua.filter(question_id=quest.id)
                        if span:
                            for i in span:
                                qo_serializer = QuestionOptionsSerializer(qo.filter(id=i.question_option_id.id).first())
                                to_data['answers'].append(qo_serializer.data)
                        else:
                            to_data['answers'].append('Нет ответа')
                    else:
                        span = ua.filter(question_id=quest.id).first()
                        if span:
                            to_data['answers'].append(span.user_answer)
                        else:
                            to_data['answers'].append('Нет ответа')
                    data['questions'].append(to_data)
                dict_with_polls['polls'].append(data)
            return Response(dict_with_polls, status=status.HTTP_200_OK)
        else:
            return Response({'errors': 'Пользователь не авторизован'}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        answers = request.data.get('answers')
        if request.user.is_authenticated:
            answers['user_id'] = request.user.id
        else:
            answers['user_id'] = User.objects.get(username='anonymous').id
        question_check = Question.objects.filter(id=answers['question_id']).first()
        ids_to_add = answers['question_option_id']
        if question_check.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
            if 'user_answer' in answers.keys():
                del (answers['user_answer'])
            for id_to_add in ids_to_add:
                answers['question_option_id'] = id_to_add
                serializer = self.serializer_class(data=answers)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        else:
            if 'question_option_id' in answers.keys():
                del (answers['question_option_id'])
            serializer = self.serializer_class(data=answers)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({'answers': 'Данные сохранены.'}, status=status.HTTP_201_CREATED)
