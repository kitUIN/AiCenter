from rest_framework import serializers

from center.models import AIModel, Worker
from center.models.workflow import TrainFile, TrainPlan, AiModelPower, AiModelPowerApiKey, TrainTask
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
    task_name = serializers.CharField(source='task.name', read_only=True)
    ai_model = serializers.IntegerField(source='task.ai_model.id', allow_null=True, read_only=True)
    ai_model_name = serializers.CharField(source='task.ai_model.name', read_only=True)

    class Meta:
        model = AiModelPower
        fields = "__all__"


class TrainTaskArgsSerializer(CustomModelSerializer):
    class Meta:
        model = TrainTask
        fields = [
            "name",
            "number",
            "status",
            "finished_datetime",
        ]


class TrainPlanArgsSerializer(CustomModelSerializer):
    class Meta:
        model = TrainPlan
        fields = [
            "name"
        ]


class AiModelPowerArgsSerializer(CustomModelSerializer):
    ai_model = serializers.IntegerField(source='task.ai_model.id', allow_null=True, read_only=True)
    ai_model_name = serializers.CharField(source='task.ai_model.name', read_only=True)

    def to_representation(self, instance: AiModelPower):
        rep = super().to_representation(instance)
        del rep["args"]
        rep["task"] = TrainTaskArgsSerializer(instance.task, read_only=True).data
        rep["plan"] = TrainPlanArgsSerializer(instance.task.plan, read_only=True).data
        return rep

    class Meta:
        model = AiModelPower
        fields = "__all__"


class AiModelPowerUpdateSerializer(CustomModelSerializer):
    class Meta:
        model = AiModelPower
        fields = ["name"]


def get_arg(body: list[dict], dep: int = 0):
    res = []
    for i in body:
        res.append("  " * dep + f"- `{i['name']}` ({i['arg_type']}) {'' if i['required'] else '**Required** '}{i['description']}")
        res += get_arg(i['children'], dep + 1)
    if dep > 0:
        return res
    return "\n".join(res)


class AiModelPowerRetrieveSerializer(CustomModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    ai_model = serializers.IntegerField(source='task.ai_model.id', allow_null=True, read_only=True)
    ai_model_name = serializers.CharField(source='task.ai_model.name', read_only=True)

    def to_representation(self, instance: AiModelPower):
        rep = super().to_representation(instance)
        doc = []
        if Worker.is_active(instance.key):
            worker = Worker.objects.get(id=instance.key)
            res = worker.get_api_doc()
            if res['code'] != 200:
                raise Exception(res['msg'])
            arg = res["data"]
            doc.append({
                "name": arg["name"],
                "api": arg["api"],
                "method": arg["method"],
                "content_type": arg["content_type"],
                "description": arg['description'],
                "request_body": get_arg(arg["request_body"]),
                "response_body": get_arg(arg["response_body"]),
                "request_example": arg["request_example"],
                "response_example": arg["response_example"],
            })
        rep["doc"] = doc
        return rep

    class Meta:
        model = AiModelPower
        fields = "__all__"


class AiModelPowerApiKeySerializer(CustomModelSerializer):
    class Meta:
        model = AiModelPowerApiKey
        fields = "__all__"
