from django.urls import include, path

from center.views import DataSetViewSet, AIModelViewSet, TrainConfigFileViewSet, TrainPlanViewSet, TrainTaskViewSet, \
    AiModelPowerViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'ai/power', AiModelPowerViewSet)
router.register(r'ai', AIModelViewSet)
router.register(r'dataset', DataSetViewSet)
router.register(r'train/file', TrainConfigFileViewSet)
router.register(r'train/plan', TrainPlanViewSet)
router.register(r'train/task', TrainTaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
