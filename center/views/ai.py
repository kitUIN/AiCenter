import json

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import action
from rest_framework.request import Request

from center.models import AIModel, Worker
from center.models.ai import AITag
from center.models.workflow import TrainFile, TrainPlan, AiModelPowerApiKey
from center.serializers import AIModelSerializer, TrainFileSerializer
from center.serializers.ai import TrainPlanSerializer, TrainFileSimpleSerializer
from sdk.plugin_tool import get_predict_kwargs
from utils import ListResponse, DetailResponse, ErrorResponse
from utils.jenkins import get_jenkins_manager
from utils.viewset import CustomModelViewSet


def get_predict_kwargs(args: str) -> dict:
    kwargs = {}
    if args:
        for arg in json.loads(args):
            if arg["type"] == "file":
                file_id = arg["value"].split("#")[-1]
                file = TrainFile.objects.filter(id=file_id).first()
                kwargs[arg["name"]] = file.file.path
            else:
                kwargs[arg["name"]] = arg["value"]
    return kwargs


class AIModelViewSet(CustomModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer

    def create(self, request: Request, *args, **kwargs):
        """新增"""
        data = request.data.copy()
        tags_data = data.get("tags", [])
        if tags_data:
            existing_tags = set(AITag.objects.filter(id__in=tags_data).values_list('id', flat=True))
            new_tags = [AITag(id=tag_id) for tag_id in tags_data if tag_id not in existing_tags]
            if new_tags:
                AITag.objects.bulk_create(new_tags)
        serializer = self.get_serializer(data=data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")

    @action(methods=["GET", "POST"], detail=True)
    def plan(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        if request.method == "GET":
            queryset = instance.plans.all()
            if queryset is not None:
                serializer = TrainPlanSerializer(self.paginate_queryset(queryset), many=True, request=request)
                return self.get_paginated_response(serializer.data)
            serializer = TrainPlanSerializer(queryset, many=True, request=request)
            return ListResponse(data=serializer.data, msg="获取成功")
        else:
            data = request.data.copy()
            args = get_predict_kwargs(data.get("args", "[]"))
            if args and "#CUSTOM_ENV_ARGS#" not in data["startup"]:
                return ErrorResponse(msg="您使用了脚本参数,但是并没有在脚本中添加#CUSTOM_ENV_ARGS#,请确认")
            startup = data["startup"].replace('#CUSTOM_ENV_ARGS#',
                                              "\n".join([f"        {k} = \"{v}\"" for k, v in args.items()]))
            flag, msg = get_jenkins_manager().create_job(data["name"], startup)
            if not flag:
                return ErrorResponse(msg=msg)
            data["ai_model"] = instance.id
            serializer = TrainPlanSerializer(data=data, request=request)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return DetailResponse(data=serializer.data, msg="新增成功")

    @action(methods=["POST"], detail=True, url_path="plan/(?P<plan_id>[^/.]+)/delete")
    def plan_delete(self, request, plan_id, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        plan = TrainPlan.objects.filter(ai_model_id=instance.id, id=plan_id).first()
        if plan:
            plan.delete()
            return DetailResponse(msg="删除成功")
        return ErrorResponse(msg="计划不存在")

    @action(methods=["GET"], detail=True)
    def file(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        queryset = instance.files.all()
        if queryset is not None:
            serializer = TrainFileSerializer(self.paginate_queryset(queryset), many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = TrainFileSerializer(queryset, many=True, request=request)
        return ListResponse(data=serializer.data, msg="获取成功")

    @action(methods=["GET"], detail=True, url_path="file/simple")
    def file_simple(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        queryset = instance.files.all()
        serializer = TrainFileSimpleSerializer(queryset, many=True, request=request)
        return DetailResponse(data=serializer.data, msg="获取成功")

    @action(methods=["POST"], detail=True, url_path="file/(?P<file_id>[^/.]+)/delete")
    def file_delete(self, request, file_id, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        file = TrainFile.objects.filter(ai_model_id=instance.id, id=file_id).first()
        if file:
            file.delete()
            return DetailResponse(msg="删除成功")
        return ErrorResponse(msg="文件不存在")

    @action(methods=["POST"], detail=True)
    def upload(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        files = request.FILES.getlist('files')  # type: list[InMemoryUploadedFile]
        file_data = []
        for file in files:
            serializer = TrainFileSerializer(
                data={'file': file,
                      'ai_model': instance.id,
                      'file_name': file.name},
                request=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            file_data.append(serializer.data)
        return DetailResponse(data=file_data, msg="上传成功")

    @action(methods=["GET"], detail=False, url_path="key")
    def key_simple(self, request, *args, **kwargs):
        keys = [
            {
                "key": w.id,
                "icon": None,
                "info": w.name
            }
            for w in Worker.active_all()
        ]
        return DetailResponse(data=keys, msg="获取成功")

    @action(methods=["GET"], detail=True, url_path="cmd")
    def cmd_template(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        if not Worker.is_active(instance.key):
            return ErrorResponse(msg="插件服务不在线")
        worker = Worker.objects.get(id=instance.key)
        res = worker.get_plan_template()
        if res['code'] != 200:
            return ErrorResponse(msg=res['msg'])

        return DetailResponse(data=res["data"], msg="获取成功")

    def predict(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return ErrorResponse(msg="缺少身份认证", code=401, status=401)
        token = auth_header[7:] if auth_header.startswith('Bearer ') else None
        api_key = AiModelPowerApiKey.objects.filter(id=token).first()
        if not api_key or (api_key and not api_key.status):
            return ErrorResponse(msg="无效的身份认证", code=401, status=401)
        power = api_key.power
        power_args = get_predict_kwargs(power.args)
        p_file = []
        files = request.FILES.getlist('files')  # type: list[InMemoryUploadedFile]
        for file in files:
            p_file.append(("files", (file.name, file.open("rb").read())))
        text = request.data.get("text")
        if not Worker.is_active(api_key.key):
            return ErrorResponse(msg="插件服务不在线")
        worker = Worker.objects.get(id=api_key.key)
        res = worker.predict(p_file, power_args)
        return DetailResponse(data=res["data"], msg=res["msg"])
