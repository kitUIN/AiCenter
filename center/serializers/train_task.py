from rest_framework import serializers

from center.models import TrainTask
from enums import TrainTaskStatus
from utils.serializers import CustomModelSerializer


class TrainTaskSerializer(CustomModelSerializer):
    ai_model_name = serializers.CharField(source="ai_model.name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    def to_representation(self, instance: TrainTask):
        rep = super().to_representation(instance)
        rep["name"] = f"{instance.plan.name} #{instance.id}"
        if instance.status == TrainTaskStatus.Canceled:
            rep["running_status"] = "已取消"
        elif instance.status == TrainTaskStatus.Running:
            if instance.log.venv == TrainTaskStatus.Running:
                rep["running_status"] = "创建虚拟环境中"
            elif instance.log.requirements == TrainTaskStatus.Running:
                rep["running_status"] = "安装依赖"
            elif instance.log.main == TrainTaskStatus.Running:
                rep["running_status"] = "训练中"
            else:
                rep["running_status"] = "运行中"
        elif instance.status == TrainTaskStatus.Succeed:
            rep["running_status"] = "训练完成"
        else:
            rep["running_status"] = "排队中"
        return rep

    class Meta:
        model = TrainTask
        fields = "__all__"
