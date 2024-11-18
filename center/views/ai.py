from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from center.models import AIModel
from center.serializers import AIModelSerializer, TrainFileSerializer
from utils.viewset import CustomModelViewSet


class AIModelViewSet(CustomModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer

    @action(methods=["POST"], detail=True)
    def upload(self, request, *args, **kwargs):
        instance = self.get_object()  # type: AIModel
        files = request.FILES.getlist('files')
        file_data = []

        for file in files:
            serializer = TrainFileSerializer(
                data={'file': file,
                      'ai_model': instance.id,
                      'file_name': file.name},
                request=request)
            if serializer.is_valid():
                serializer.save()
                file_data.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'uploaded_files': file_data}, status=status.HTTP_201_CREATED)
