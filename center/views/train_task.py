from rest_framework.decorators import action
from rest_framework.request import Request

from center.models import TrainTask
from center.serializers import TrainTaskSerializer
from center.serializers.train_task import TrainTaskLogSerializer
from enums import TrainTaskStatus
from utils import DetailResponse
from utils.viewset import CustomModelViewSet
from pathlib import Path


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

    @action(methods=["GET"], detail=True, url_path="log/detail")
    def log_detail(self, request, *args, **kwargs):
        task = self.get_object()  # type: TrainTask
        line = request.query_params.get("pos")
        log_type = request.query_params.get("log_type", "")
        env_name = f"train_task/{task.plan.name}_{task.id}"
        current_pos = None
        lines = []
        if log_type == "requirements":
            file_name = Path(f"{env_name}/requirements.out")
            with file_name.open("r", encoding="utf8") as f:
                if line and line != "0":
                    f.seek(int(line))
                lines = f.readlines()
                current_pos = f.tell()
        return DetailResponse(msg="获取成功", data={
            "pos": current_pos,
            "lines": [i.rstrip("\n") for i in lines]
        })
