from django.urls import path
import api.views as views

app_name = 'api'

urlpatterns = [
    path('users/login/', views.UserLoginAPIView.as_view()),
    path('users/register/', views.UserRegistrationAPIView.as_view()),
    path('users/', views.UserRetrieveUpdateAPIView.as_view()),
    path('users/answers/', views.UserAnswersAPIView.as_view()),
    path('polls/', views.PollsAPIView.as_view()),
    path('polls/<int:pk>', views.PollsAPIView.as_view()),
    path('polls/one/<int:pk>', views.PollsOneAPIView.as_view()),
    path('questions/', views.QuestionAPIView.as_view()),
    path('questions/<int:pk>', views.QuestionAPIView.as_view()),
    path('questionOptions/<int:pk>', views.QuestionOptionsAPIView.as_view()),
]
