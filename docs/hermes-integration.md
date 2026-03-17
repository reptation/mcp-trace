# Hermes Integration

## Overview

`mcp-trace` integrates with Hermes via MCP to record and inspect **a single agent run locally**.

The goal is simple:

> capture what happened during one run, and make it easy to inspect

This includes:

- when the run started
- reasoning steps
- tool calls
- tool results
- errors
- final status

---

## What You Get

With `mcp-trace` connected, you can answer:

- What did the agent try to do?
- Which tools were called?
- What did those tools return?
- Where did the run fail?
- What happened just before the failure?

This is especially useful when Hermes outputs something like:

```text
Error: tool execution failed
```

Instead of guessing, you can inspect the full timeline.

---

## Architecture

At a high level:

```text
Hermes Agent
|
| MCP tool calls
v
mcp-trace server
|
v
SQLite / Postgres
|
v
local inspection (UI or MCP tools)
```

Hermes calls `mcp-trace` tools during execution to log events.

---

## Prerequisites

- Python 3.10+
- `mcp-trace` installed locally
- Hermes configured to use MCP servers
- SQLite is sufficient for first use

---

## Step 1: Start `mcp-trace`

From the repository:

```bash
cd server
pip install -e .
mcp-trace
```

You should see logs like:

```text
Starting mcp-trace
DB: sqlite:///trace.db
```

Leave this running.

---

## Step 2: Configure Hermes to Use `mcp-trace`

Add `mcp-trace` as an MCP server in your Hermes configuration.

Example:

```yaml
mcp_servers:
  trace:
    command: mcp-trace
```

If Hermes requires explicit Python invocation:

```yaml
mcp_servers:
  trace:
    command: python
    args:
      - -m
      - mcp_trace.main
```

After starting Hermes, it should discover these tools:

- `start_run`
- `log_event`
- `finish_run`
- `get_run`
- `list_runs`

---

## Step 3: Verify the Connection

Start Hermes and confirm:

- no MCP startup errors
- `mcp-trace` logs show activity
- Hermes can see the trace tools

If tools are not visible:

- check the command path
- confirm `mcp-trace` runs independently
- check Hermes logs for MCP errors

---

## Step 4: Logging a Run

A single run should follow this sequence:

1. `start_run`
2. multiple `log_event` calls
3. `finish_run`

Example flow:

```text
start_run("hermes", "Investigate checkout latency")

log_event(..., "reasoning", ...)
log_event(..., "tool_call", ...)
log_event(..., "tool_result", ...)
log_event(..., "error", ...)

finish_run(..., "failed")
```

This produces a complete timeline.

---

## Step 5: Example Debugging Scenario

Prompt:

```text
Investigate why checkout-api latency increased today
```

Recorded timeline:

```text
run_started
reasoning      "Checking recent deployments"
tool_call      get_recent_deployments
tool_result    found deployment 17 minutes ago
reasoning      "Inspecting logs"
tool_call      get_logs
tool_result    rate limit exceeded
error          failed to retrieve logs
run_finished   failed
```

This makes the failure obvious:

- the logs tool failed

---

## Step 6: Inspecting Runs

### Option A: Via MCP Tools

Use:

- `list_runs`
- `get_run`

Example:

```text
list_runs(limit=5)
get_run(run_id="run_123")
```

### Option B: Via Web UI

If enabled, open the local UI to:

- view recent runs
- inspect timelines
- identify failures quickly

---

## Step 7: Recommended Workflow

For development:

1. start `mcp-trace`
2. start Hermes with MCP enabled
3. run a single task
4. inspect the run
5. fix tools or prompts
6. rerun

This loop is the core use case.

---

## Minimal Integration Strategy

For early usage, you do not need deep Hermes changes.

You can:

- manually trigger trace tools
- lightly modify agent prompts or tools to include tracing calls

Later, this can be automated with:

- wrappers around tool execution
- middleware inside Hermes
- agent runtime hooks

---

## Common Issues

### `mcp-trace` Not Starting

- check the Python environment
- verify dependencies are installed
- run `python -m mcp_trace.main`

### Hermes Cannot See Tools

- verify MCP server config
- check the command path
- confirm the server is running

### No Runs Recorded

- ensure `start_run` is called
- confirm `log_event` is being used
- check that the database file exists

---

## Future Improvements

This initial integration is intentionally simple.

Future improvements may include:

- automatic tracing of all tool calls
- automatic run lifecycle management
- richer payloads such as latency and token usage
- trace export and sharing
- integration with external observability systems

---

## Summary

The Hermes integration is built around a simple idea:

1. start a run
2. record events
3. finish the run
4. inspect the timeline

This is enough to make agent behavior visible and debuggable.

`mcp-trace` turns a failed agent run into a readable story.
