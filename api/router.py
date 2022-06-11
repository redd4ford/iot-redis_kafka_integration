from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from api.views import DatasetProcessorAPIView

urlpatterns = [
    path(
        r"dataset-processor/load/",
        DatasetProcessorAPIView.as_view(),
        name="dataset_processor",
    )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
