from asyncio import current_task

from sqlalchemy import create_engine, NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)
from sqlalchemy.orm import sessionmaker

from config import (
    ASYNC_DATABASE_CONN_URL,
    DATABASE_CONN_URL,
    DATABASE_CONN_POOL_SIZE,
)

async_engine = create_async_engine(
    ASYNC_DATABASE_CONN_URL,
    pool_size=DATABASE_CONN_POOL_SIZE,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
)


engine = create_engine(
    DATABASE_CONN_URL,
    pool_size=DATABASE_CONN_POOL_SIZE,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async_scope_engine = create_async_engine(
    ASYNC_DATABASE_CONN_URL,
    future=True,
    poolclass=NullPool,
    pool_pre_ping=True,
)
async_scope_session_factory = async_sessionmaker(
    async_scope_engine,
    expire_on_commit=False,
)

AsyncScopedSession = async_scoped_session(
    async_scope_session_factory, scopefunc=current_task
)


async def get_async_db_session():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
