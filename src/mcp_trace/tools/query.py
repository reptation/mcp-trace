from __future__ import annotations

from typing import Any

from mcp_trace.server import get_run_store, mcp


@mcp.tool()
def get_run(run_id: str) -> dict[str, Any]:
    return get_run_store().get_run(run_id)


@mcp.tool()
def list_runs(
    limit: int = 10,
    status: str | None = None,
    agent_name: str | None = None,
) -> list[dict[str, Any]]:
    return get_run_store().list_runs(
        limit=limit,
        status=status,
        agent_name=agent_name,
    )
