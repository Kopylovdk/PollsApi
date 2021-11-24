from rest_framework import serializers
from django.contrib.auth import authenticate
from api.models import User, Poll, Question, UsersAnswers, QuestionOptions


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя"""
    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'token']

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        if username is None:
            raise serializers.ValidationError(
                'Заполните поле логин'
            )
        if password is None:
            raise serializers.ValidationError(
                'Заполните поле паорль'
            )
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                'Такого пользователя не существует.'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'Пользователь деактивирован'
            )

        return {'username': user.username,
                'token': user.token
                }


class UserSerializer(serializers.ModelSerializer):
    """ Ощуществляет сериализацию и десериализацию объектов User. """
    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token', 'first_name', 'last_name', )
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """ Выполняет обновление User. """
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class GlobalSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class PollsSerializer(GlobalSerializer):
    class Meta:
        model = Poll
        fields = '__all__'

    def create(self, validated_data):
        return Poll.objects.create(**validated_data)


class QuestionSerializer(GlobalSerializer):
    class Meta:
        model = Question
        fields = '__all__'

    def create(self, validated_data):
        return Question.objects.create(**validated_data)


class QuestionOptionsSerializer(GlobalSerializer):
    class Meta:
        model = QuestionOptions
        fields = '__all__'

    def create(self, validated_data):
        return QuestionOptions.objects.create(**validated_data)


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersAnswers
        fields = '__all__'

    def create(self, validated_data):
        return UsersAnswers.objects.create(**validated_data)