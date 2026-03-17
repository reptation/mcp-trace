from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp_trace.database import configure_engine, init_db
from mcp_trace.storage.run_store import RunStore


class RunStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.db_path = Path(self.tmp_dir.name) / "trace.db"
        configure_engine(f"sqlite:///{self.db_path}")
        init_db()
        self.store = RunStore()

    def test_start_run_creates_running_run(self) -> None:
        run = self.store.start_run(
            agent_name="hermes",
            task="Investigate checkout latency",
            user_id="user-1",
            session_id="session-1",
            metadata={"env": "test"},
        )

        self.assertTrue(run["run_id"].startswith("run_"))
        self.assertEqual(run["status"], "running")
        self.assertEqual(run["metadata"], {"env": "test"})
        self.assertIsNone(run["finished_at"])

    def test_append_event_uses_monotonic_sequence(self) -> None:
        run = self.store.start_run(agent_name="hermes", task="Sequence test")

        first = self.store.append_event(
            run_id=run["run_id"],
            event_type="reasoning",
            payload={"message": "step 1"},
            step_index=1,
        )
        second = self.store.append_event(
            run_id=run["run_id"],
            event_type="tool_call",
            payload={"tool": "get_logs"},
            step_index=2,
        )

        self.assertEqual(first["sequence"], 1)
        self.assertEqual(second["sequence"], 2)

    def test_finish_run_and_get_run_return_ordered_timeline(self) -> None:
        run = self.store.start_run(agent_name="hermes", task="Timeline test")
        run_id = run["run_id"]

        self.store.append_event(
            run_id=run_id,
            event_type="reasoning",
            payload={"message": "Checking deployments"},
            step_index=1,
        )
        self.store.append_event(
            run_id=run_id,
            event_type="tool_call",
            payload={"tool": "get_recent_deployments"},
            step_index=2,
        )
        self.store.append_event(
            run_id=run_id,
            event_type="tool_result",
            payload={"result": "deployment found"},
            step_index=3,
        )
        finished = self.store.finish_run(
            run_id=run_id,
            status="completed",
            output_summary="Investigation finished",
            metadata={"resolution": "rollback"},
        )

        timeline = self.store.get_run(run_id)
        runs = self.store.list_runs(limit=5, status="completed", agent_name="hermes")

        self.assertEqual(finished["status"], "completed")
        self.assertEqual(timeline["run"]["status"], "completed")
        self.assertEqual(timeline["run"]["metadata"], {"resolution": "rollback"})
        self.assertEqual(
            [event["sequence"] for event in timeline["events"]],
            [1, 2, 3, 4],
        )
        self.assertEqual(
            [event["event_type"] for event in timeline["events"]],
            ["reasoning", "tool_call", "tool_result", "run_finished"],
        )
        self.assertEqual(runs[0]["run_id"], run_id)


if __name__ == "__main__":
    unittest.main()
