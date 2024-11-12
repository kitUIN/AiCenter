from rest_framework import serializers

from center.models import TrainConfigFile
from utils.serializers import CustomModelSerializer


class TrainConfigFileSerializer(CustomModelSerializer):
    class Meta:
        model = TrainConfigFile
        fields = "__all__"
