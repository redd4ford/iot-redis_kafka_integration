from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from injector import inject
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from api.exceptions import (
    LinkDoesNotContainJsonError,
    HttpErrorOnProcessingError,
    JsonDecodeError,
)
from app_services.dataset_processor import DatasetProcessor
from app_services.infrastructure import RedisService


class DatasetProcessorAPIView(APIView):
    """
    Link-based dataset processor.
    """

    def __init__(self, service: DatasetProcessor = DatasetProcessor(), *args, **kwargs):
        super(DatasetProcessorAPIView, self).__init__(**kwargs)
        self.service = service

    def dispatch(self, request, *args, **kwargs):
        return super(DatasetProcessorAPIView, self).dispatch(request, *args, **kwargs)

    @inject
    def setup(self, request, service: DatasetProcessor = DatasetProcessor(), *args, **kwargs):
        super(DatasetProcessorAPIView, self).setup(request, service, args, kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "link", OpenApiTypes.STR, OpenApiParameter.QUERY,
                required=True,
                description="A path to the .json file",
                default=settings.DEFAULT_DATASET,
            ),
            OpenApiParameter(
                "ignore_status", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                required=True,
                description="Process the file again even if it was processed before",
                default=False,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(response=HTTP_200_OK, description="File processed"),
            400: OpenApiResponse(description="Bad request"),
        },
    )
    def post(self, request):
        """
        Get dataset from a link, write data to Kafka or Console (see settings.WRITE_TO_KAFKA),
        and store file processing status in Redis.
        """
        try:
            result = self.service.run(**request.query_params)
        except LinkDoesNotContainJsonError as e:
            return Response(
                {"message": e.message},
                status=HTTP_404_NOT_FOUND
            )
        except (HttpErrorOnProcessingError, JsonDecodeError) as e:
            return Response(
                {"message": e.message},
                status=HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"message": f"File processed: {request.query_params.get('link')}, status={result}"},
                status=HTTP_200_OK
            )


class FileStatusCheckerAPIView(APIView):
    """
    Check the current file processing status.
    """

    def __init__(self, service: RedisService = RedisService(), *args, **kwargs):
        super(FileStatusCheckerAPIView, self).__init__(**kwargs)
        self.service = service

    def dispatch(self, request, *args, **kwargs):
        return super(FileStatusCheckerAPIView, self).dispatch(request, *args, **kwargs)

    @inject
    def setup(self, request, service: RedisService = RedisService(), *args, **kwargs):
        super(FileStatusCheckerAPIView, self).setup(request, service, args, kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "link", OpenApiTypes.STR, OpenApiParameter.QUERY,
                required=True,
                description="A path to the .json file that is currently being processed",
                default=settings.DEFAULT_DATASET,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(response=HTTP_200_OK, description="File processed"),
            400: OpenApiResponse(description="Bad request"),
        },
    )
    def get(self, request):
        try:
            link = (
                request.query_params.get("link")[0]
            )
            if not link.endswith(".json"):
                raise LinkDoesNotContainJsonError(link)
            result = self.service.get(link)
            if not result:
                raise