# Data Model

## Purpose

`mcp-trace` is designed to make it easy to inspect **one agent run locally**.

The data model is intentionally small. It is built around a simple idea:

- one **run**
- many **events** inside that run

This keeps the first version easy to understand, easy to query, and easy to render in a debugger-style UI.

---

## Design Principles

### 1. Optimize for local debugging
The first goal is to answer:

> What happened during this run?

Not:

- cross-service distributed tracing
- large-scale telemetry analytics
- multi-tenant observability pipelines

Those may come later, but they are out of scope for the initial model.

### 2. Use an append-only event timeline
Agent execution is naturally sequential:

- a run begins
- the agent reasons
- the agent calls tools
- the agent receives results
- the run finishes or fails

Representing execution as a sequence of events is simpler than inventing many specialized tables up front.

### 3. Prefer a small core schema with flexible payloads
Different agents and tools may emit different details. Rather than hard-coding every possible field into the schema, `mcp-trace` stores core metadata in fixed columns and event details in JSON payloads.

### 4. Keep ordering deterministic
Event timestamps alone are not enough to guarantee a stable timeline. The model includes a monotonic `sequence` field per run so events can always be displayed in the exact order they were recorded.

---

## Core Entities

`mcp-trace` has two primary entities:

- `Run`
- `Event`

### Run

A `Run` represents one agent attempt to complete one task.

Examples:

- "Investigate why checkout-api latency increased today"
- "Summarize the README in this repository"
- "Check recent deployments and identify likely causes of failure"

A run is the top-level unit shown in the debugger.

### Event

An `Event` represents one thing that happened during a run.

Examples:

- the run started
- the agent recorded a reasoning step
- the agent called a tool
- a tool returned a result
- an error occurred
- the run finished

Events are displayed in order to form the run timeline.

---

## Run Schema

The `Run` entity should contain the following fields.

| Field | Type | Description |
|---|---|---|
| `run_id` | string | Stable unique identifier for the run |
| `agent_name` | string | Name of the agent that created the run, such as `hermes` |
| `task` | string | Human-readable description of the task |
| `status` | string | Current run status: `running`, `completed`, `failed`, or `cancelled` |
| `user_id` | string nullable | Optional user identifier |
| `session_id` | string nullable | Optional session identifier |
| `metadata` | JSON nullable | Optional extra metadata for the run |
| `started_at` | datetime | When the run started |
| `finished_at` | datetime nullable | When the run ended |

### Notes

#### `run_id`
This should be a stable external identifier, not just an auto-increment integer. The UI and MCP tools should refer to runs by `run_id`.

Example:

```text
run_01hxyzabc123

