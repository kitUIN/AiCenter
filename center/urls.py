from django.urls import include, path

from center.views.dataset import DataSetViewSet
from center.views.ai import AIModelViewSet
from center.views.train_config_file import TrainConfigFileViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'ai', AIModelViewSet)
router.register(r'dataset', DataSetViewSet)
router.register(r'train/file', TrainConfigFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
