from rest_framework import serializers

from center.models import TrainTask
from utils.serializers import CustomModelSerializer


class TrainTaskSerializer(CustomModelSerializer):
    ai_model_name = serializers.CharField(source="ai_model.name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    def to_representation(self, instance: TrainTask):
        rep = super().to_representation(instance)
        rep["name"] = f"{instance.plan.name} #{instance.id}"
        return rep

    class Meta:
        model = TrainTask
        fields = "__all__"
