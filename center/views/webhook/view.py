import logging

from rest_framework.viewsets import ModelViewSet

from center.models import DataSet
from center.serializers import DataSetSerializer
from utils import DetailResponse, retry_save

logger = logging.getLogger(__name__)


@retry_save()
def update_dataset_num(dataset_id: int, task_number: int, finished_task_number: int, total_predictions_number: int,
                       total_annotations_number: int, skipped_annotations_number: int):
    dataset = DataSet.objects.filter(id=dataset_id).first()  # type: DataSet
    if dataset:
        dataset.task_number = task_number
        dataset.finished_task_number = finished_task_number
        dataset.total_predictions_number = total_predictions_number
        dataset.total_annotations_number = total_annotations_number
        dataset.skipped_annotations_number = skipped_annotations_number
        dataset.save()


class WebHookViewSet(ModelViewSet):
    serializer_class = DataSetSerializer

    def TASKS_CREATED(self, data):
        project = data['project']
        update_dataset_num(project['id'],
                           task_number=project['task_number'],
                           finished_task_number=project['finished_task_number'],
                           total_predictions_number=project['total_predictions_number'],
                           total_annotations_number=project['total_annotations_number'],
                           skipped_annotations_number=project['skipped_annotations_number'],
                           )

    def ANNOTATIONS_DELETED(self, data):
        self.TASKS_CREATED(data)

    def TASKS_DELETED(self, data):
        self.TASKS_CREATED(data)

    def label_studio(self, request, *arg, **kwargs):
        logger.info(request.query_params)
        logger.info(request.data)
        data = request.data.copy()
        action = data.get('action')
        action_method = getattr(self, action, None)
        if action_method:
            action_method(data)
        return DetailResponse(msg="ok")
