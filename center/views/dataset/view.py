import logging
from datetime import timedelta

from rest_framework.request import Request

from center.models import DataSet
from center.serializers import DataSetSerializer
from center.serializers.dataset import DataSetCreateSerializer
from center.views.dataset.tool import label_studio_create_project
from utils import DetailResponse, CustomModelViewSet, ErrorResponse
from label_studio_sdk.core.api_error import ApiError

logger = logging.getLogger(__name__)


class DataSetViewSet(CustomModelViewSet):
    values_queryset = DataSet.objects.all()
    queryset = values_queryset
    serializer_class = DataSetSerializer
    create_serializer_class = DataSetCreateSerializer

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        try:
            _id = label_studio_create_project(data["name"], data["description"])
        except ApiError as e:
            return ErrorResponse(msg=f"{e}")
        data["id"] = _id
        logger.info(data)
        serializer = self.get_serializer(data=data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")
