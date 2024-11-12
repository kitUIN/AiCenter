from rest_framework import serializers

from center.models import AIModel
from utils.serializers import CustomModelSerializer


class AIModelSerializer(CustomModelSerializer):
    class Meta:
        model = AIModel
        fields = "__all__"
