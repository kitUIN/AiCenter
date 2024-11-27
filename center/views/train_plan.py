from rest_framework.decorators import action

from center.models import TrainPlan
from center.serializers import TrainPlanSerializer, TrainTaskSerializer
from enums.viewset_method import ViewSetRequestMethod
from utils import DetailResponse
from utils.viewset import CustomModelViewSet


class TrainPlanViewSet(CustomModelViewSet):
    queryset = TrainPlan.objects.all()
    serializer_class = TrainPlanSerializer
    exclude_methods = [ViewSetRequestMethod.Create, ViewSetRequestMethod.Destroy]

    @action(methods=["POST"], detail=True, url_path="start")
    def start(self, request, *args, **kwargs):
        instance = self.get_object()  # type: TrainPlan
        serializer = TrainTaskSerializer(data={
            "ai_model": instance.ai_model_id,
            "plan": instance.id
        }, request=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DetailResponse(msg="启动成功")
