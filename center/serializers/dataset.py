import base64

from rest_framework import serializers

from application.settings import LABEL_STUDIO_URL
from center.models import DataSet
from utils.serializers import CustomModelSerializer


class DataSetSerializer(CustomModelSerializer):

    def to_representation(self, instance) -> dict:
        rep = super().to_representation(instance)
        middle_url = f"/user/login/?next=/projects/{instance.id}/data"
        rep["middle_url"] = LABEL_STUDIO_URL + "/api/ai/center/node/?url=" + base64.b64encode(
            middle_url.encode()).decode()
        return rep

    class Meta:
        model = DataSet
        fields = "__all__"


class DataSetCreateSerializer(CustomModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = DataSet
        fields = ["id", "name", "description"]
        extra_kwargs = {'id': {'required': False}}
