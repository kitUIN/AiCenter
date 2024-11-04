from django.urls import include, path

from center.views.train_config import TrainConfigViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'train/config', TrainConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
