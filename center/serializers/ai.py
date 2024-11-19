from rest_framework import serializers

from center.models import AIModel
from center.models.workflow import TrainFile, TrainPlan
from utils.serializers import CustomModelSerializer


class AIModelSerializer(CustomModelSerializer):
    class Meta:
        model = AIModel
        fields = "__all__"


class TrainFileSerializer(CustomModelSerializer):
    class Meta:
        model = TrainFile
        fields = "__all__"


class TrainPlanSerializer(CustomModelSerializer):
    class Meta:
        model = TrainPlan
        fields = "__all__"
