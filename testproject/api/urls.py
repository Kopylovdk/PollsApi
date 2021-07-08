from django.urls import path
import api.views as views

app_name = 'api'

urlpatterns = [
    path('users/login/', views.UserLoginAPIView.as_view()),
    path('users/register/', views.UserRegistrationAPIView.as_view()),
    path('users/update/', views.UserRetrieveUpdateAPIView.as_view()),
    path('users/user/', views.UserRetrieveUpdateAPIView.as_view()),

    path('users/answers/', views.UserAnswersAPIView.as_view()),

    path('polls/create/', views.PollsAPIView.as_view()),
    path('polls/update/<int:pk>', views.PollsAPIView.as_view()),           #
    path('polls/list/', views.PollsAPIView.as_view()),
    path('polls/activeList/', views.PollsActiveListAPIView.as_view()),
    path('polls/<int:pk>/', views.PollsOneAPIView.as_view()),             #

    path('questions/', views.QuestionAPIView.as_view()),
    path('questions/<int:pk>', views.QuestionAPIView.as_view()),     #

    path('questionOptions/', views.QuestionOptionsAPIView.as_view()),
]
