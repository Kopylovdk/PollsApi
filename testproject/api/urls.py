from django.urls import path
import api.views as views

app_name = 'api'

urlpatterns = [
    path('users/login/', views.UserLoginAPIView.as_view()),
    path('users/register/', views.UserRegistrationAPIView.as_view()),
    path('users/update/', views.UserRetrieveUpdateAPIView.as_view()),
    path('users/user/', views.UserRetrieveUpdateAPIView.as_view()),
    path('users/answersCreate/', views.UserAnswersAPIView.as_view()),
    path('users/answersList/', views.UserAnswersAPIView.as_view()),
    path('polls/create/', views.PollsAPIView.as_view()),
    path('polls/update/', views.PollsAPIView.as_view()),
    path('polls/list/', views.PollsAPIView.as_view()),
    path('polls/getOnePollOrActiveList/', views.PollsListAPIView.as_view()),
    path('questions/create/', views.QuestionAPIView.as_view()),
    path('questions/update/', views.QuestionAPIView.as_view()),
    path('questionOptions/create/', views.QuestionOptionsAPIView.as_view()),
    path('questionOptions/update/', views.QuestionOptionsAPIView.as_view()),
]
