from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from center.models import AIModel
from center.models.ai import AITag
from center.models.workflow import TrainFile, TrainPlan
from center.serializers import AIModelSerializer, TrainFileSerializer
from center.serializers.ai import TrainPlanSerializer, TrainFileSimpleSerializer
from plugin.plugin_tool import get_plugin_templates
from utils import ListResponse, DetailResponse, ErrorResponse
from utils.viewset import CustomModelViewSet


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
                "key": k,
                "icon": v._icon,
                "info": v._info
            }
            for k, v in get_plugin_templates().items()
        ]
        return DetailResponse(data=keys, msg="获取成功")

    @action(methods=["GET"], detail=True, url_path="cmd")
    def cmd_template(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        templates = get_plugin_templates()
        if instance.key not in templates.keys():
            return ErrorResponse(msg="找不到对应的命令模板")
        template_class = templates[instance.key]
        template = template_class()
        data = template.get_plan()
        return DetailResponse(data=data, msg="获取成功")
