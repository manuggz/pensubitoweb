# coding=utf-8
from rest_framework import serializers

from api_misvoti.models import MiVotiUser


class UserSerializer(serializers.ModelSerializer):
    plan_json = serializers.StringRelatedField(source='gdrive_id_json_plan')

    class Meta:
        model = MiVotiUser
        fields = ('username', 'carnet', 'cedula', 'plan_json')
