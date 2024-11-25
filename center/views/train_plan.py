from center.models import TrainPlan
from center.serializers import TrainPlanSerializer
from enums.viewset_method import ViewSetRequestMethod
from utils.viewset import CustomModelViewSet


class TrainPlanViewSet(CustomModelViewSet):
    queryset = TrainPlan.objects.all()
    serializer_class = TrainPlanSerializer
    exclude_methods = [ViewSetRequestMethod.Create, ViewSetRequestMethod.Destroy]
