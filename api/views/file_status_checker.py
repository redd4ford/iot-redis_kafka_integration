from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
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
    FileStatusNotFoundError,
)

from app_services.infrastructure import RedisService


class FileStatusCheckerAPIView(APIView):
    """
    Check the current file processing status.
    """

    def __init__(self, service: RedisService = RedisService(), *args, **kwargs):
        super(FileStatusCheckerAPIView, self).__init__(*args, **kwargs)
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
            200: OpenApiResponse(response=HTTP_200_OK,
                                 description="OK: Link and processing status"),
            400: OpenApiResponse(response=HTTP_400_BAD_REQUEST,
                                 description="Bad request: There is no dataset by this link"),
            404: OpenApiResponse(response=HTTP_404_NOT_FOUND,
                                 description="Not found: There is no status recorded in Redis"),
        },
    )
    def get(self, request):
        """
        Get the current file processing status by its link.
        """
        try:
            link = (
                request.query_params.get("link")
            )

            if not link.endswith(".json"):
                raise LinkDoesNotContainJsonError(link)

            result = self.service.get(link)

            if not result:
                raise FileStatusNotFoundError
        except LinkDoesNotContainJsonError as e:
            return Response(
                {"message": e.message},
                status=HTTP_400_BAD_REQUEST
            )
        except FileStatusNotFoundError as e:
            return Response(
                {"message": e.message},
                status=HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                {"message": f"File={link}, status={result}"},
                status=HTTP_200_OK
            )
