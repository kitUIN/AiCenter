from center.models import AIModel
from center.serializers import AIModelSerializer
from utils.viewset import CustomModelViewSet


class AIModelViewSet(CustomModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
