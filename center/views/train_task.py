from center.models import TrainTask
from center.serializers import TrainTaskSerializer
from utils.viewset import CustomModelViewSet


class TrainTaskViewSet(CustomModelViewSet):
    queryset = TrainTask.objects.all()
    serializer_class = TrainTaskSerializer

