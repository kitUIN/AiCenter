from rest_framework.decorators import action

from center.models import TrainPlan, TrainTask
from center.serializers import TrainPlanSerializer, TrainTaskSerializer
from enums.viewset_method import ViewSetRequestMethod
from utils import DetailResponse
from utils.jenkins import get_jenkins_manager
from utils.viewset import CustomModelViewSet
from center.tasks import start_train


class TrainPlanViewSet(CustomModelViewSet):
    queryset = TrainPlan.objects.all()
    serializer_class = TrainPlanSerializer
    exclude_methods = [ViewSetRequestMethod.Create, ViewSetRequestMethod.Destroy]

    @action(methods=["POST"], detail=True, url_path="start")
    def start(self, request, *args, **kwargs):
        plan = self.get_object()  # type: TrainPlan
        server = get_jenkins_manager().server
        next_build_number = server.get_job_info(plan.name)['nextBuildNumber']
        TrainTask.objects.create(plan_id=plan.id, ai_model_id=plan.ai_model_id, number=next_build_number)
        server.build_job(plan.name)
        return DetailResponse(msg="启动成功")
