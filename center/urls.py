from django.urls import include, path

from center.views.dataset import DataSetViewSet
from center.views.ai import AIModelViewSet
from utils import OptionalSlashRouter

router = OptionalSlashRouter()
router.register(r'ai', AIModelViewSet)
router.register(r'dataset', DataSetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
