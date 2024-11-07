from rest_framework import serializers

from center.models import DataSet
from utils.serializers import CustomModelSerializer


class DataSetSerializer(CustomModelSerializer):
    class Meta:
        model = DataSet
        fields = "__all__"


class DataSetCreateSerializer(CustomModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = DataSet
        fields = "__all__"
        extra_kwargs = {'id': {'required': False}}
