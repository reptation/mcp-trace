from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: int | None = Field(default=None, primary_key=True)
    run_id: str = Field(
        sa_column=Column(String, nullable=False, unique=True, index=True)
    )
    agent_name: str = Field(sa_column=Column(String, nullable=False, index=True))
    task: str = Field(sa_column=Column(Text, nullable=False))
    status: str = Field(sa_column=Column(String, nullable=False, index=True))
    user_id: str | None = Field(default=None, sa_column=Column(String, nullable=True))
    session_id: str | None = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )
    metadata_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    started_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    finished_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class Event(SQLModel, table=True):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_events_run_sequence"),
    )

    id: int | None = Field(default=None, primary_key=True)
    event_id: str = Field(
        sa_column=Column(String, nullable=False, unique=True, index=True)
    )
    run_id: str = Field(sa_column=Column(String, nullable=False, index=True))
    sequence: int = Field(sa_column=Column(Integer, nullable=False))
    event_type: str = Field(sa_column=Column(String, nullable=False, index=True))
    step_index: int | None = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    severity: str | None = Field(
        default=None,
        sa_column=Column(String, nullable=True),
    )
    payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
