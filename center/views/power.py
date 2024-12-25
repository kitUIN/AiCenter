import json
import uuid

from center.models import Worker
from center.models.workflow import AiModelPower, AiModelPowerApiKey
from center.serializers import AiModelPowerSerializer, AiModelPowerApiKeySerializer, AiModelPowerRetrieveSerializer
from center.serializers.ai import AiModelPowerUpdateSerializer, AiModelPowerArgsSerializer
from plugin import get_plugin_templates, ArgData
from utils import DetailResponse, ErrorResponse
from utils.viewset import CustomModelViewSet
from rest_framework.decorators import action


class AiModelPowerViewSet(CustomModelViewSet):
    queryset = AiModelPower.objects.all()
    serializer_class = AiModelPowerSerializer
    retrieve_serializer_class = AiModelPowerRetrieveSerializer
    update_serializer_class = AiModelPowerUpdateSerializer

    @action(methods=["GET", "POST"], detail=True)
    def key(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AiModelPower
        if request.method == "GET":
            queryset = instance.keys.all()
            serializer = AiModelPowerApiKeySerializer(queryset, many=True, request=request)
            return DetailResponse(data=serializer.data, msg="获取成功")
        else:
            data = request.data.copy()
            key_id = uuid.uuid4().hex + uuid.uuid4().hex
            while AiModelPowerApiKey.objects.filter(key=key_id).exists():
                key_id = uuid.uuid4().hex + uuid.uuid4().hex
            data["id"] = key_id
            data["power"] = instance.id
            data["key"] = instance.task.ai_model.key
            serializer = AiModelPowerApiKeySerializer(data=data, request=request)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return DetailResponse(data=serializer.data, msg="新增成功")

    @action(methods=["POST"], detail=True, url_path="key/(?P<key_id>[^/.]+)/delete")
    def key_delete(self, request, key_id, *args, **kwargs):
        instance = self.get_object()  # type: AiModelPower
        key = AiModelPowerApiKey.objects.filter(power_id=instance.id, id=key_id).first()
        if key:
            key.delete()
            return DetailResponse(msg="删除成功")
        return ErrorResponse(msg="密钥不存在")

    @action(methods=["GET", "POST"], detail=True, url_path="args")
    def args(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AiModelPower
        if request.method == "GET":
            if instance.configured:
                return DetailResponse(msg="查询成功", data=json.loads(instance.args))
            if not Worker.is_active(instance.key):
                return ErrorResponse(msg="插件服务不在线")
            worker = Worker.objects.get(id=instance.key)
            data = AiModelPowerArgsSerializer(instance).data
            res = worker.get_power_args(data)
            if res['code'] != 200:
                return ErrorResponse(msg=res['msg'])
            return DetailResponse(msg="查询成功", data=res['data'])
        else:
            req_args_string = request.data.get("args")
            if not req_args_string:
                return ErrorResponse(msg="缺少参数")
            req_args = [ArgData(**i) for i in json.loads(req_args_string)]
            required = [arg.name for arg in args if arg.required]
            req_arg_names = [arg.name for arg in req_args]
            for required_arg in required:
                if required_arg not in req_arg_names:
                    return ErrorResponse(msg=f"缺失必要参数:{required_arg}")
            AiModelPower.objects.filter(id=instance.id).update(args=req_args_string, configured=True)
            return DetailResponse(msg="配置成功")
