from center.models import TrainConfig
from center.serializers.train_config import TrainConfigSerializer
from utils.viewset import CustomModelViewSet


class TrainConfigViewSet(CustomModelViewSet):
    values_queryset = TrainConfig.objects.all()
    queryset = values_queryset
    serializer_class = TrainConfigSerializer
