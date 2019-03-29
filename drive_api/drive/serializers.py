from rest_framework import serializers
from .models import Resources
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = '__all__'
