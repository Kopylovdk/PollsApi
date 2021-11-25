from django.urls import path
import api.views as views

app_name = 'api'

urlpatterns = [
    path('users/login/', views.UserLoginAPIView.as_view(), name='login'),
    path('users/register/', views.UserRegistrationAPIView.as_view(), name='register'),
    path('users/', views.UserRetrieveUpdateAPIView.as_view(), name='data'),

    path('users/polls/', views.UserAnswersAPIView.as_view(), name='user_polls_get'),

    path('polls/', views.PollsAPIView.as_view(), name='poll'),
    path('polls/<int:pk>', views.PollsAPIView.as_view(), name='poll_pk'),

    path('questions/<int:pk>', views.QuestionAPIView.as_view(), name='question'),
    path('questions/<int:pk>/answers/', views.UserAnswersAPIView.as_view(), name='user_question_answer'),

    path('question_options/<int:pk>', views.QuestionOptionsAPIView.as_view(),
         name='question_options_create_update_delete'),
]
