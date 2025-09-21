from http import HTTPStatus

from fastapi.exceptions import RequestValidationError
from fastapi_babel import _
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.common.loggers import logger
from core.common.exceptions import HRSystemBaseException


def base_error_handler(request: Request, exception: HRSystemBaseException):
    logger.exception(msg="Error", exc_info=exception)

    status_code = (
        exception.code
        if isinstance(exception, HRSystemBaseException)
        else HTTPStatus.INTERNAL_SERVER_ERROR
    )
    message, param = (
        (exception.message, exception.kwargs)
        if isinstance(exception, HRSystemBaseException)
        else (_("Internal Server Error"), None)
    )
    if param is not None:
        if isinstance(param, dict):
            message = message.format(**param)
        elif isinstance(param, (list, tuple, set)):
            message = message.format(*param)
        else:
            message = message.format(param)

    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "errors": message,
        },
    )


def validation_exception_handler(request: Request, exception: RequestValidationError):
    logger.debug(msg="Validation Error", exc_info=exception)

    errs = []
    for err in exception.errors():
        if err["type"] == "value_error":
            error_ctx = err.get("ctx", {}).get("error")
            error_message = str(error_ctx) if error_ctx else err.get("msg")
            error_key = (
                err.get("loc")[1] if len(err.get("loc")) > 1 else err.get("loc")[0]
            )
            errs.append({error_key: error_message})
        else:
            errs.append({err["loc"][0]: err.get("msg")})

    return JSONResponse(status_code=400, content={"errors": errs})


def sqlalchemy_exception_handler(request: Request, exception: SQLAlchemyError):
    logger.exception(msg=f"SQLAlchemy error: {request.url}", exc_info=exception)

    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={
            "status_code": HTTPStatus.BAD_REQUEST,
            "errors": "Bad request!",
        },
    )
