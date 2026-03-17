from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    agent_name: str
    task: str
    status: str
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] | None = None
    started_at: datetime
    finished_at: datetime | None = None


class EventRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    run_id: str
    sequence: int
    event_type: str
    step_index: int | None = None
    severity: str | None = None
    payload: dict[str, Any]
    created_at: datetime


class RunTimeline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run: RunRecord
    events: list[EventRecord]


class StartRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: str


class LogEventResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    event_id: str


class FinishRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    run_id: str
    status: str
