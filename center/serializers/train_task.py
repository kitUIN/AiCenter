from rest_framework import serializers

from application.settings import JENKINS_URL
from center.models import TrainTask
from enums import TrainTaskStatus
from utils.serializers import CustomModelSerializer


class TrainTaskSerializer(CustomModelSerializer):
    ai_model_name = serializers.CharField(source="ai_model.name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    def to_representation(self, instance: TrainTask):
        rep = super().to_representation(instance)
        rep["log_url"] = f"{JENKINS_URL}/job/{instance.plan.name}/{instance.number}/pipeline-console/"
        if instance.status == TrainTaskStatus.Canceled:
            rep["running_status"] = "已取消"
        elif instance.status == TrainTaskStatus.Running:
            rep["running_status"] = "运行中"
        elif instance.status == TrainTaskStatus.Succeed:
            rep["running_status"] = "已完成"
            rep["res_url"] = f"{JENKINS_URL}/job/{instance.plan.name}/{instance.number}/artifact/"
        elif instance.status == TrainTaskStatus.Fail:
            rep["running_status"] = "失败"
        else:
            rep["running_status"] = "排队中"
        return rep

    class Meta:
        model = TrainTask
        fields = "__all__"


