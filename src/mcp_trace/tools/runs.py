from __future__ import annotations

from typing import Any

from mcp_trace.schemas import FinishRunResult, LogEventResult, StartRunResult
from mcp_trace.server import get_run_store, mcp


@mcp.tool()
def start_run(
    agent_name: str,
    task: str,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run = get_run_store().start_run(
        agent_name=agent_name,
        task=task,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata,
    )
    return StartRunResult(run_id=run["run_id"], status="started").model_dump(mode="json")


@mcp.tool()
def log_event(
    run_id: str,
    event_type: str,
    payload: dict[str, Any],
    step_index: int | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    event = get_run_store().append_event(
        run_id=run_id,
        event_type=event_type,
        payload=payload,
        step_index=step_index,
        severity=severity,
    )
    return LogEventResult(ok=True, event_id=event["event_id"]).model_dump(mode="json")


@mcp.tool()
def finish_run(
    run_id: str,
    status: str,
    output_summary: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run = get_run_store().finish_run(
        run_id=run_id,
        status=status,
        output_summary=output_summary,
        metadata=metadata,
    )
    return FinishRunResult(ok=True, run_id=run_id, status=run["status"]).model_dump(
        mode="json"
    )
