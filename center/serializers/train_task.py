from datetime import datetime

from rest_framework import serializers

from center.models import TrainTask
from center.models.workflow import TrainTaskLog
from enums import TrainTaskStatus
from utils.serializers import CustomModelSerializer
import pytz

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
            elif instance.log.train == TrainTaskStatus.Running:
                rep["running_status"] = "训练中"
            else:
                rep["running_status"] = "运行中"
        elif instance.status == TrainTaskStatus.Succeed:
            rep["running_status"] = "训练完成"
        elif instance.status == TrainTaskStatus.Fail:
            rep["running_status"] = "失败"
        else:
            rep["running_status"] = "排队中"
        return rep

    class Meta:
        model = TrainTask
        fields = "__all__"


class TrainTaskLogSerializer(CustomModelSerializer):
    def to_representation(self, instance: TrainTaskLog):
        rep = super().to_representation(instance)
        rep["venv_seconds"] = 0
        rep["requirements_seconds"] = 0
        rep["train_seconds"] = 0
        now = datetime.now(tz=pytz.timezone('UTC'))
        if instance.venv_start_datetime:
            if instance.venv_end_datetime:
                rep["venv_seconds"] = (instance.venv_end_datetime - instance.venv_start_datetime).seconds
            else:
                rep["venv_seconds"] = (now - instance.venv_start_datetime).seconds
        if instance.requirements_start_datetime:
            if instance.requirements_end_datetime:
                rep["requirements_seconds"] = (instance.requirements_end_datetime - instance.requirements_start_datetime).seconds
            else:
                rep["requirements_seconds"] = (now - instance.requirements_start_datetime).seconds

        if instance.train_start_datetime:
            if instance.train_end_datetime:
                rep["train_seconds"] = (instance.train_end_datetime - instance.train_start_datetime).seconds
            else:
                rep["train_seconds"] = (now - instance.train_start_datetime).seconds
        rep["total_seconds"] = rep["venv_seconds"] + rep["requirements_seconds"] + rep["train_seconds"]
        return rep

    class Meta:
        model = TrainTaskLog
        fields = "__all__"
