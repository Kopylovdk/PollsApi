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


class PollsAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PollsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def get(self, request, pk=None):
        if pk is not None:
            poll = get_object_or_404(Poll, id=pk, is_active=True)
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
        elif request.user.is_superuser:
            polls = Poll.objects.all()
            serializer = self.serializer_class(polls, many=True)
            return Response({'polls': serializer.data}, status=status.HTTP_200_OK)
        else:
            polls = Poll.objects.filter(is_active=True)
            serializer = self.serializer_class(polls, many=True)
            return Response({'polls': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_superuser:
            poll = request.data.get('polls')
            serializer = self.serializer_class(data=poll)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'polls': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk):
        if request.user.is_superuser:
            if not request.data:
                return Response({'errors': 'No data'}, status=status.HTTP_400_BAD_REQUEST)
            new_poll = request.data.get('polls')
            poll = get_object_or_404(Poll, id=pk)
            keys = new_poll.keys()
            if 'start_date' in keys:
                del (new_poll['start_date'])
            serializer = self.serializer_class(instance=poll, data=new_poll, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        if request.data:
            return Response({'errors': 'JSON not available'}, status=status.HTTP_400_BAD_REQUEST)
        poll = get_object_or_404(Poll, id=pk)
        if poll.is_active:
            p_deactivation(False, poll)
        else:
            p_deactivation(True, poll)
        return Response({'detail': f'Active change to {poll.is_active}'}, status.HTTP_200_OK)


def p_deactivation(choice, poll):
    poll.is_active = choice
    poll.save()
    q_deactivation(choice, p_id=poll.id)


class QuestionAPIView(APIView):
    permission_classes = (IsAdminUser,)
    serializer_class = QuestionSerializer
    renderer_classes = (ClassJSONRenderer,)

    def post(self, request, pk):
        question = request.data.get('question')
        question_options = request.data.get('question_options')
        if question:
            question['poll_id'] = get_object_or_404(Poll, pk=pk).id
            if question['question_type'] in ['MANY_ANSWERS', 'ONE_ANSWER'] and not question_options:
                return Response({'errors': 'question_options is missing'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'errors': 'question is missing'}, status=status.HTTP_403_FORBIDDEN)
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
        if not request.data:
            return Response({'errors': 'No data'}, status=status.HTTP_400_BAD_REQUEST)
        new_question = request.data.get('question')
        q = get_object_or_404(Question, id=pk)
        serializer = self.serializer_class(instance=q, data=new_question, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request, pk):
        if request.data:
            return Response({'errors': 'JSON not available'}, status=status.HTTP_400_BAD_REQUEST)
        q = get_object_or_404(Question, id=pk)
        if q.is_active:
            q_deactivation(choice=False, q_obj=q)
        else:
            q_deactivation(choice=True, q_obj=q)
        return Response({'detail': f'Active change to {q.is_active}'}, status.HTTP_200_OK)


def q_deactivation(choice, p_id=None, q_obj=None):
    if p_id:
        for q in Question.objects.filter(poll_id=p_id):
            q.is_active = choice
            q.save()
            if q.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
                qo_deactivation(choice=q.is_active, q_id=q.id)
    else:
        q_obj.is_active = choice
        q_obj.save()
        if q_obj.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
            qo_deactivation(choice=q_obj.is_active, q_id=q_obj.id)


class QuestionOptionsAPIView(APIView):
    permission_classes = (IsAdminUser,)
    serializer_class = QuestionOptionsSerializer
    renderer_classes = (ClassJSONRenderer,)

    def post(self, request, pk):
        question_options = request.data.get('question_options')
        question_options['question_id'] = pk
        serializer = self.serializer_class(data=question_options)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'question_options': serializer.data}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        new_qo = request.data.get('question_options')
        qo = get_object_or_404(QuestionOptions, id=pk)
        serializer = self.serializer_class(instance=qo, data=new_qo, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'question_options': serializer.data}, status.HTTP_200_OK)

    def delete(self, request, pk):
        if request.data:
            return Response({'errors': 'JSON not available'}, status=status.HTTP_400_BAD_REQUEST)
        qo = get_object_or_404(QuestionOptions, id=pk)
        if qo.is_active:
            qo_deactivation(choice=False, qo_obj=qo)
        else:
            qo_deactivation(choice=True, qo_obj=qo)
        return Response({'detail': f'Active change to {qo.is_active}'}, status.HTTP_200_OK)


def qo_deactivation(choice, q_id=None, qo_obj=None):
    if q_id:
        for qo in QuestionOptions.objects.filter(question_id=q_id):
            qo.is_active = choice
            qo.save()
    else:
        qo_obj.is_active = choice
        qo_obj.save()


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
                            to_data['answers'].append('No answer')
                    else:
                        span = ua.filter(question_id=quest.id).first()
                        if span:
                            to_data['answers'].append(span.user_answer)
                        else:
                            to_data['answers'].append('No answer')
                    data['questions'].append(to_data)
                dict_with_polls['polls'].append(data)
            return Response(dict_with_polls, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

    def post(self, request, pk):
        answers = request.data.get('answers')
        if answers:
            q = get_object_or_404(Question, id=pk)
            answers['question_id'] = q.id
            answers['poll_id'] = q.poll_id.id
        else:
            return Response({'errors': 'answers is missing'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.is_authenticated:
            answers['user_id'] = request.user.id
        else:
            answers['user_id'] = User.objects.get(username='anonymous').id
        if q.question_type in ['MANY_ANSWERS', 'ONE_ANSWER']:
            if not answers['question_option_id']:
                return Response({'errors': 'question_option_id is missing'}, status=status.HTTP_403_FORBIDDEN)
            ids_to_add = []
            for i in answers['question_option_id']:
                ids_to_add.append(get_object_or_404(QuestionOptions, id=i).id)
            if 'user_answer' in answers.keys():
                del (answers['user_answer'])
            for id_to_add in ids_to_add:
                answers['question_option_id'] = id_to_add
                serializer = self.serializer_class(data=answers)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        else:
            if not answers['user_answer']:
                return Response({'errors': 'user_answer is missing'}, status=status.HTTP_403_FORBIDDEN)
            if 'question_option_id' in answers.keys():
                del (answers['question_option_id'])
            serializer = self.serializer_class(data=answers)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({'answers': 'Data saved'}, status=status.HTTP_201_CREATED)
