import logging

from config import LOGGER_LEVEL, LOGGER_FORMAT, SQLALCHEMY_LOG_LEVEL

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": LOGGER_FORMAT},
    },
    "level": LOGGER_LEVEL,
    "handlers": {
        "default": {
            "level": LOGGER_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {
            "level": LOGGER_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": LOGGER_LEVEL,
            "handlers": ["default"],
        },
        "uvicorn.access": {
            "level": LOGGER_LEVEL,
            "handlers": ["default"],
        },
        "sqlalchemy.engine": {
            "level": SQLALCHEMY_LOG_LEVEL,
            "handlers": ["default"],
        },
    },
}

if hasattr(logging, "config"):
    logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)
