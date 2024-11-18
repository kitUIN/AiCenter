from rest_framework.decorators import action

from center.models import TrainConfigFile
from center.serializers import TrainConfigFileSerializer
from utils.viewset import CustomModelViewSet


class TrainConfigFileViewSet(CustomModelViewSet):
    queryset = TrainConfigFile.objects.all()
    serializer_class = TrainConfigFileSerializer

