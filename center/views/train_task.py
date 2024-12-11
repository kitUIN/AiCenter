import logging
from datetime import datetime

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.request import Request

from center.models import TrainTask, TrainPlan
from center.serializers import TrainTaskSerializer
from center.serializers.train_task import TrainTaskLogSerializer
from enums import TrainTaskStatus
from utils import DetailResponse, ErrorResponse
from utils.jenkins import get_jenkins_manager
from utils.viewset import CustomModelViewSet
from pathlib import Path

logger = logging.getLogger(__name__)


class TrainTaskViewSet(CustomModelViewSet):
    queryset = TrainTask.objects.all()
    serializer_class = TrainTaskSerializer
    # filter_backends = [SearchFilter]
    filterset_fields = ['plan', ]

    def destroy(self, request: Request, *args, **kwargs):
        instance = self.get_object()  # type: TrainTask
        get_jenkins_manager().stop_build(instance)
        return DetailResponse(data=[], msg="发起中断任务成功")

    @action(methods=["GET"], detail=True, url_path="log")
    def log(self, request, *args, **kwargs):
        instance = self.get_object()  # type: TrainTask
        serializer = TrainTaskLogSerializer(instance, request=request)
        return DetailResponse(msg="获取成功", data=serializer.data)

    @action(methods=["POST"], detail=False)
    def notify(self, request, *args, **kwargs):
        logger.info(request.data)
        logger.info(request.POST)
        return DetailResponse(msg="获取成功")

    @action(methods=["POST"], detail=False, url_path="notify/queue")
    def notify_queue(self, request, *args, **kwargs):
        logger.info(request.data)
        logger.info(request.POST)
        return DetailResponse(msg="获取成功")

    @action(methods=["POST"], detail=False, url_path="notify/build")
    def notify_build(self, request, *args, **kwargs):
        logger.info(request.data)
        data = request.data.copy()
        plan = TrainPlan.objects.filter(name=data["fullJobName"]).first()
        if not plan:
            return ErrorResponse(msg="找不到该计划")
        if data["result"] == "INPROGRESS":
            TrainTask.objects.update_or_create(plan_id=plan.id, ai_model_id=plan.ai_model_id, number=data["number"],
                                               defaults={
                                                   'status': TrainTaskStatus.Running
                                               })
        elif data["result"] == "SUCCESS":
            TrainTask.objects.filter(plan_id=plan.id, number=data["number"]).update(
                finished_datetime=datetime.fromtimestamp(data["endTime"] / 1000.0),
                status=TrainTaskStatus.Succeed)
        elif data["result"] == "ABORTED":
            TrainTask.objects.filter(plan_id=plan.id, number=data["number"]).update(
                status=TrainTaskStatus.Canceled)
        return DetailResponse(msg="获取成功")

    @action(methods=["GET"], detail=True, url_path="log/detail")
    def log_detail(self, request, *args, **kwargs):
        task = self.get_object()  # type: TrainTask
        line = request.query_params.get("pos")
        log_type = request.query_params.get("log_type", "")
        log_name = f"train_task/{task.plan.name}_{task.id}/logs/{log_type}.out"
        current_pos = None
        lines = []
        if log_type != "venv":
            file_name = Path(log_name)
            with file_name.open("r", encoding="utf8") as f:
                if line and line != "0":
                    f.seek(int(line))
                lines = f.readlines()
                current_pos = f.tell()
        return DetailResponse(msg="获取成功", data={
            "log_type": log_type,
            "pos": current_pos,
            "lines": [i.rstrip("\n") for i in lines]
        })
