import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware

import config

from api.common.handlers import base_error_handler, sqlalchemy_exception_handler, validation_exception_handler
from app.api.v1.routers import router
from core.common.exceptions import HRSystemBaseException

app = FastAPI(
    title="Anyjob Corporation service",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(HRSystemBaseException, base_error_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, base_error_handler)

app.include_router(router, prefix="/api")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.API_PORT, reload=True)