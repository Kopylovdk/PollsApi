from main.settings import DEBUG
if DEBUG:
    from api.models import User, Poll, Question, QuestionOptions, UsersAnswers
    from django.contrib import admin


    @admin.register(User)
    class PollAdmin(admin.ModelAdmin):
        list_display = ('username',)
        list_filter = ('is_active',)

    @admin.register(Poll)
    class PollAdmin(admin.ModelAdmin):
        list_display = ('name',)
        list_filter = ('is_active', )


    @admin.register(Question)
    class QuestionAdmin(admin.ModelAdmin):
        list_display = ('question_text',)
        list_filter = ('is_active', )


    @admin.register(QuestionOptions)
    class QuestionOptionsAdmin(admin.ModelAdmin):
        list_display = ('question_answer',)
        list_filter = ('is_active',)


    @admin.register(UsersAnswers)
    class UsersAnswersAdmin(admin.ModelAdmin):
        list_display = ('user_id', 'user_answer',)
