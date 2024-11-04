from rest_framework import serializers

from center.models import TrainConfig
from utils.serializers import CustomModelSerializer


class TrainConfigSerializer(CustomModelSerializer):
    class Meta:
        model = TrainConfig
        fields = "__all__"
