# mcp-trace

`mcp-trace` records one agent run and lets you inspect it as an ordered timeline.

It is a local-first MCP server built for the simplest debugging loop:

- start one run
- record events inside that run
- inspect the ordered timeline

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
mcp-trace
```

By default, `mcp-trace` creates a local SQLite database at `trace.db`.

## Available Tools

- `start_run`: create a new run and mark it as `running`
- `log_event`: append an event to a run using a monotonic sequence number
- `finish_run`: mark the run complete, failed, or cancelled and record a `run_finished` event
- `get_run`: fetch one run and all of its events in sequence order
- `list_runs`: list recent runs, optionally filtered by status or agent name

## Local Configuration

Environment variables are optional:

- `MCP_TRACE_DB_URL`
- `MCP_TRACE_LOG_LEVEL`

Defaults:

- `db_url = sqlite:///trace.db`
- `log_level = INFO`

## Development Notes

The backend is intentionally small:

- SQLite-backed storage via `sqlmodel`
- one `Run` model
- one `Event` model
- five MCP tools

The key design rule is:

> one run -> ordered events -> readable timeline

## Smoke Test

After installing dependencies, you can exercise the storage layer directly:

```bash
python scripts/smoke_test.py
```

This will create a run, append example events, finish the run, and print the timeline.
