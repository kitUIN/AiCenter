import uuid

from center.models.workflow import AiModelPower, AiModelPowerApiKey
from center.serializers import AiModelPowerSerializer,AiModelPowerApiKeySerializer, AiModelPowerRetrieveSerializer
from utils import DetailResponse, ErrorResponse
from utils.viewset import CustomModelViewSet
from rest_framework.decorators import action


class AiModelPowerViewSet(CustomModelViewSet):
    queryset = AiModelPower.objects.all()
    serializer_class = AiModelPowerSerializer
    retrieve_serializer_class = AiModelPowerRetrieveSerializer
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


