import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi_babel import BabelConfigs
from sqlalchemy import URL
from starlette.templating import Jinja2Templates

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()

ENVIRONMENT = os.getenv("ENVIRONMENT")

API_SECRET_KEY = os.getenv("API_SECRET_KEY")

JWT_ACCESS_SECRET_KEY = os.getenv("JWT_ACCESS_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRED = int(os.getenv("ACCESS_TOKEN_EXPIRED"))
REFRESH_TOKEN_EXPIRED = int(os.getenv("REFRESH_TOKEN_EXPIRED"))


LOGGER_FORMAT = os.getenv("LOGGER_FORMAT")
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL")
SQLALCHEMY_LOG_LEVEL = os.getenv("SQLALCHEMY_LOG_LEVEL", "INFO")

CORS_ALLOWED_ORIGINS: list = [
    *(filter(lambda x: len(x) > 0, os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")))
]

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_CONN_POOL_SIZE = int(os.getenv("DATABASE_CONN_POOL_SIZE", 10))

ASYNC_DATABASE_CONN_URL = URL.create(
    "postgresql+asyncpg",
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
)

DATABASE_CONN_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE"))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
babel_configs = BabelConfigs(
    ROOT_DIR=Path(__file__).resolve(),
    BABEL_DEFAULT_LOCALE=os.getenv("BABEL_DEFAULT_LOCALE", default="en"),
    BABEL_TRANSLATION_DIRECTORY=os.path.join(BASE_DIR, "i18n"),
)

API_PORT = int(os.getenv("API_PORT"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Google API Scopes
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

LANGUAGE_MESSAGE = "ja"
DEFAULT_TIMEZONE_SERVER = os.getenv("DEFAULT_TIMEZONE_SERVER", "UTC")
DEFAULT_TIMEZONE_USER = os.getenv("DEFAULT_TIMEZONE_USER", "Asia/Tokyo")

UPLOAD_CLOUD_TARGET = os.getenv("UPLOAD_CLOUD_TARGET", "false").lower() == "true"
