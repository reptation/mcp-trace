from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_trace.storage.run_store import RunStore

mcp = FastMCP("mcp-trace")
_run_store: RunStore | None = None


def set_run_store(run_store: RunStore) -> None:
    global _run_store
    _run_store = run_store


def get_run_store() -> RunStore:
    global _run_store
    if _run_store is None:
        _run_store = RunStore()
    return _run_store
