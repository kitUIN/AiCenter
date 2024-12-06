from rest_framework import serializers

from center.models import AIModel
from center.models.ai import AITag
from center.models.workflow import TrainFile, TrainPlan, AiModelPower, AiModelPowerApiKey
from utils.serializers import CustomModelSerializer


class AIModelSerializer(CustomModelSerializer):
    class Meta:
        model = AIModel
        fields = "__all__"


class TrainFileSerializer(CustomModelSerializer):
    class Meta:
        model = TrainFile
        fields = "__all__"


class TrainFileSimpleSerializer(CustomModelSerializer):
    class Meta:
        model = TrainFile
        fields = "__all__"


class TrainPlanSerializer(CustomModelSerializer):
    class Meta:
        model = TrainPlan
        fields = "__all__"


class AiModelPowerSerializer(CustomModelSerializer):
    class Meta:
        model = AiModelPower
        fields = "__all__"


class AiModelPowerRetrieveSerializer(CustomModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    ai_model = serializers.IntegerField(source='task.ai_model.id', allow_null=True, read_only=True)
    ai_model_name = serializers.CharField(source='task.ai_model.name', read_only=True)

    class Meta:
        model = AiModelPower
        fields = "__all__"


class AiModelPowerApiKeySerializer(CustomModelSerializer):
    class Meta:
        model = AiModelPowerApiKey
        fields = "__all__"
