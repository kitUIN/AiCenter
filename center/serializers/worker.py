from center.models import Worker
from utils.serializers import CustomModelSerializer


class WorkerSerializer(CustomModelSerializer):
    class Meta:
        model = Worker
        fields = "__all__"
