from rest_framework import serializers

from application.settings import JENKINS_URL
from center.models import TrainTask
from center.models.workflow import TrainTaskStep
from center.tasks.workflow import get_now
from enums import TrainTaskStatus
from utils.serializers import CustomModelSerializer


class TrainTaskSerializer(CustomModelSerializer):
    ai_model_name = serializers.CharField(source="ai_model.name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    def to_representation(self, instance: TrainTask):
        rep = super().to_representation(instance)
        rep["name"] = f"{instance.plan.name} #{instance.number}"
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


class TrainTaskStepSerializer(CustomModelSerializer):
    def to_representation(self, instance: TrainTaskStep):
        rep = super().to_representation(instance)
        if instance.start_datetime:
            rep["seconds"] = (
                    (instance.end_datetime if instance.end_datetime else get_now()) - instance.start_datetime).seconds
        else:
            rep["seconds"] = 0
        return rep

    class Meta:
        model = TrainTaskStep
        fields = "__all__"


class TrainTaskLogSerializer(CustomModelSerializer):
    def to_representation(self, instance: TrainTask):
        rep = super().to_representation(instance)
        rep["steps"] = TrainTaskStepSerializer(instance.steps, request=self.request, many=True).data
        rep["total_seconds"] = sum(i["seconds"] for i in rep["steps"])
        return rep

    class Meta:
        model = TrainTask
        fields = "__all__"

#
# class TrainTaskLogSerializer(CustomModelSerializer):
#     def to_representation(self, instance: TrainTaskLog):
#         rep = super().to_representation(instance)
#         now = datetime.now(tz=pytz.timezone('UTC'))
#         if instance.venv_start_datetime:
#             if instance.venv_end_datetime:
#                 rep["venv_seconds"] = (instance.venv_end_datetime - instance.venv_start_datetime).seconds
#             else:
#                 rep["venv_seconds"] = (now - instance.venv_start_datetime).seconds
#         if instance.requirements_start_datetime:
#             if instance.requirements_end_datetime:
#                 rep["requirements_seconds"] = (
#                             instance.requirements_end_datetime - instance.requirements_start_datetime).seconds
#             else:
#                 rep["requirements_seconds"] = (now - instance.requirements_start_datetime).seconds
#
#         if instance.train_start_datetime:
#             if instance.train_end_datetime:
#                 rep["train_seconds"] = (instance.train_end_datetime - instance.train_start_datetime).seconds
#             else:
#                 rep["train_seconds"] = (now - instance.train_start_datetime).seconds
#         rep["total_seconds"] = rep["venv_seconds"] + rep["requirements_seconds"] + rep["train_seconds"]
#         return rep
#
#     class Meta:
#         model = TrainTaskLog
#         fields = "__all__"
