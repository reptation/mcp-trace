from __future__ import annotations

import json

from mcp_trace.config import get_settings
from mcp_trace.database import init_db
from mcp_trace.storage.run_store import RunStore


def main() -> None:
    settings = get_settings()
    init_db(settings)

    store = RunStore()
    run = store.start_run(
        agent_name="smoke-test",
        task="Verify the mcp-trace MVP backend",
    )
    run_id = run["run_id"]

    store.append_event(
        run_id=run_id,
        event_type="reasoning",
        payload={"message": "Planning the next step"},
        step_index=1,
    )
    store.append_event(
        run_id=run_id,
        event_type="tool_call",
        payload={"tool": "get_status", "args": {"service": "checkout-api"}},
        step_index=2,
    )
    store.append_event(
        run_id=run_id,
        event_type="tool_result",
        payload={"status": "healthy"},
        step_index=3,
    )
    store.finish_run(
        run_id=run_id,
        status="completed",
        output_summary="Smoke test completed successfully",
    )

    timeline = store.get_run(run_id)
    print(f"Run {run_id} ({timeline['run']['status']}): {timeline['run']['task']}")
    for event in timeline["events"]:
        payload = json.dumps(event["payload"], sort_keys=True)
        print(f"{event['sequence']:02d} {event['event_type']}: {payload}")


if __name__ == "__main__":
    main()
