"""HTTP controller that attaches photos to products."""

from http import HTTPStatus
from typing import final, override

from django.http import HttpResponse
from dmr import Body, Controller, modify
from dmr.endpoint import Endpoint
from dmr.errors import ErrorType
from dmr.metadata import ResponseSpec

from server.apps.catalog.logic import photos, value_objects
from server.apps.catalog.logic.usecases import attach_photo
from server.apps.catalog.public.products import UnknownProductError
from server.common.di import HasContainer
from server.common.serializers import StrictMsgspecSerializer


@final
class ProductPhoto(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Attaches photos to products over HTTP."""

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.NOT_FOUND,
            ),
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            ),
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            ),
        ],
    )
    def put(
        self, parsed_body: Body[value_objects.PhotoUpload],
    ) -> value_objects.PhotoSize:
        """Keeps the thumbnail of the photo for the product in the path."""
        return self.resolve(attach_photo.AttachPhoto)(self.kwargs['id'], parsed_body)

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[StrictMsgspecSerializer],
        exc: Exception,
    ) -> HttpResponse:
        """Answers 404, 422 or 503 for the errors of the photo."""
        match exc:
            case UnknownProductError():
                status, message, kind = (
                    HTTPStatus.NOT_FOUND,
                    'Product not found',
                    ErrorType.not_found,
                )
            case photos.BrokenPhotoError():
                status, message, kind = (
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    'The photo is not a JPEG, PNG or WebP picture',
                    ErrorType.user_msg,
                )
            case photos.ThumbnailsUnavailableError():
                status, message, kind = (
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    'Photos cannot be processed right now',
                    ErrorType.user_msg,
                )
            case _:
                return super().handle_error(endpoint, controller, exc)
        return self.to_error(
            self.format_error(message, error_type=kind),
            status_code=status,
        )
