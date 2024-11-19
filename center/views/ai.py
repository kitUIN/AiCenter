from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from center.models import AIModel
from center.models.workflow import TrainFile, TrainPlan
from center.serializers import AIModelSerializer, TrainFileSerializer
from center.serializers.ai import TrainPlanSerializer
from utils import ListResponse, DetailResponse, ErrorResponse
from utils.viewset import CustomModelViewSet


class AIModelViewSet(CustomModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer

    @action(methods=["GET"], detail=True)
    def plan(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        queryset = instance.plans.all()
        if queryset is not None:
            serializer = TrainPlanSerializer(self.paginate_queryset(queryset), many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = TrainPlanSerializer(queryset, many=True, request=request)
        return ListResponse(data=serializer.data, msg="获取成功")

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
