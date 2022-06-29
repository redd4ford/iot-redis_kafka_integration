from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from api.views import (
    DatasetProcessorAPIView,
    FileStatusCheckerAPIView,
)

urlpatterns = [
    path(
        r"dataset-processor/load/",
        DatasetProcessorAPIView.as_view(),
        name="dataset_processor",
    ),
    path(
        r"status-checker/get/",
        FileStatusCheckerAPIView.as_view(),
        name="file_status_checker",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
