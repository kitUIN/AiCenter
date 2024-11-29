from rest_framework.decorators import action
from rest_framework.request import Request

from center.models import TrainTask
from center.serializers import TrainTaskSerializer
from center.serializers.train_task import TrainTaskLogSerializer
from enums import TrainTaskStatus
from utils import DetailResponse
from utils.viewset import CustomModelViewSet


class TrainTaskViewSet(CustomModelViewSet):
    queryset = TrainTask.objects.all()
    serializer_class = TrainTaskSerializer

    def destroy(self, request: Request, *args, **kwargs):
        instance = self.get_object()  # type: TrainTask
        instance.status = TrainTaskStatus.Canceled
        instance.save()
        return DetailResponse(data=[], msg="删除成功")

    @action(methods=["GET"], detail=True, url_path="log")
    def log(self, request, *args, **kwargs):
        instance = self.get_object()  # type: TrainTask
        serializer = TrainTaskLogSerializer(instance.log, request=request)
        return DetailResponse(msg="获取成功", data=serializer.data)
