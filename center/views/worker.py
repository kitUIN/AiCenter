from center.models import Worker
from center.serializers import WorkerSerializer
from utils import CustomModelViewSet


class WorkerViewSet(CustomModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
