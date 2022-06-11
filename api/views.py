from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
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
from app_services.dataset_processor import DataProcessor


class DatasetProcessorAPIView(APIView):
    """
    Link-based dataset processor.
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "link", OpenApiTypes.STR, OpenApiParameter.QUERY,
                required=True,
                description="A path to the .json file",
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(response=HTTP_200_OK, description="Database is filled"),
            400: OpenApiResponse(description="Bad request"),
        },
    )
    def get(self, request):
        """
        Get dataset from a link, write data to Kafka or Console (see settings.WRITE_TO_KAFKA),
        and store file processing status in Redis.
        """
        try:
            DataProcessor.process(**request.query_params)
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
                {"message": f"File processed: {request.query_params.get('link')}"},
                status=HTTP_200_OK
            )
