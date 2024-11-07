from django.urls import include, path

from center.views.dataset import DataSetViewSet
from center.views.train_config import TrainConfigViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'train/config', TrainConfigViewSet)
router.register(r'dataset', DataSetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
