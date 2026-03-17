from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine

from mcp_trace.config import Settings, get_settings

_engine: Engine | None = None


def _sqlite_connect_args(db_url: str) -> dict[str, bool]:
    if db_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def configure_engine(db_url: str | None = None) -> Engine:
    global _engine

    if db_url is None:
        db_url = get_settings().db_url

    _engine = create_engine(
        db_url,
        connect_args=_sqlite_connect_args(db_url),
    )
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        return configure_engine()
    return _engine


def init_db(settings: Settings | None = None) -> None:
    if settings is not None:
        configure_engine(settings.db_url)
    else:
        get_engine()

    import mcp_trace.models  # noqa: F401

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Session:
    return Session(get_engine())
