from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from reading_list.utils.errors import (
    ConflictError,
    EntityNotFoundError,
    ServiceError,
    ValidationError,
)

DETAIL_KEY = 'detail'


async def _handle_not_found(request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={DETAIL_KEY: str(exc)},
    )


async def _handle_validation_error(request, exc: ValidationError):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={DETAIL_KEY: str(exc)},
    )


async def _handle_conflict_error(request, exc: ConflictError):
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content={DETAIL_KEY: str(exc)},
    )


async def _handle_service_error(request, exc: ServiceError):
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={DETAIL_KEY: 'Internal service error'},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EntityNotFoundError, _handle_not_found)
    app.add_exception_handler(ValidationError, _handle_validation_error)
    app.add_exception_handler(ConflictError, _handle_conflict_error)
    app.add_exception_handler(ServiceError, _handle_service_error)
