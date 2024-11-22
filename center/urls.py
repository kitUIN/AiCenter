from django.urls import include, path

from center.views.dataset import DataSetViewSet
from center.views.ai import AIModelViewSet
from center.views.train_config_file import TrainConfigFileViewSet
from center.views.train_task import TrainTaskViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'ai', AIModelViewSet)
router.register(r'dataset', DataSetViewSet)
router.register(r'train/file', TrainConfigFileViewSet)
router.register(r'train/task', TrainTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
