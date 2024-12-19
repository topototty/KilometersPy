from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'groups']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Этот адрес электронной почты уже используется.")
        return value

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        if groups_data:
            user.groups.set(groups_data)
        return user