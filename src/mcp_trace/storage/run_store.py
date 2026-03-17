from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from sqlalchemy import desc, func
from sqlmodel import Session, select

from mcp_trace.database import get_session
from mcp_trace.models import Event, Run
from mcp_trace.schemas import EventRecord, RunRecord, RunTimeline


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunStore:
    def __init__(
        self,
        session_factory: Callable[[], Session] = get_session,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self._session_factory = session_factory
        self._now = now

    def start_run(
        self,
        agent_name: str,
        task: str,
        user_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        run = Run(
            run_id=self._new_id("run"),
            agent_name=agent_name,
            task=task,
            status="running",
            user_id=user_id,
            session_id=session_id,
            metadata_json=self._dump_json(metadata),
            started_at=self._now(),
        )

        with self._session_factory() as session:
            session.add(run)
            session.commit()
            session.refresh(run)

        return self._run_dict(run)

    def append_event(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, Any],
        step_index: int | None = None,
        severity: str | None = None,
    ) -> dict[str, Any]:
        with self._session_factory() as session:
            run = self._get_run_model(session, run_id)
            max_sequence = session.exec(
                select(func.max(Event.sequence)).where(Event.run_id == run.run_id)
            ).one()
            next_sequence = int(max_sequence or 0) + 1

            event = Event(
                event_id=self._new_id("evt"),
                run_id=run.run_id,
                sequence=next_sequence,
                event_type=event_type,
                step_index=step_index,
                severity=severity,
                payload_json=self._dump_json(payload) or "{}",
                created_at=self._now(),
            )
            session.add(event)
            session.commit()
            session.refresh(event)

        return self._event_dict(event)

    def finish_run(
        self,
        run_id: str,
        status: str,
        output_summary: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._session_factory() as session:
            run = self._get_run_model(session, run_id)
            run.status = status
            run.finished_at = self._now()

            if metadata is not None:
                existing_metadata = self._load_json(run.metadata_json) or {}
                existing_metadata.update(metadata)
                run.metadata_json = self._dump_json(existing_metadata)

            session.add(run)
            session.commit()
            session.refresh(run)

        event_payload: dict[str, Any] = {"status": status}
        if output_summary is not None:
            event_payload["output_summary"] = output_summary
        if metadata is not None:
            event_payload["metadata"] = metadata

        self.append_event(run_id=run_id, event_type="run_finished", payload=event_payload)
        return self._run_dict(run)

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._session_factory() as session:
            run = self._get_run_model(session, run_id)
            events = list(
                session.exec(
                    select(Event)
                    .where(Event.run_id == run.run_id)
                    .order_by(Event.sequence)
                )
            )

        timeline = RunTimeline(
            run=self._run_record(run),
            events=[self._event_record(event) for event in events],
        )
        return timeline.model_dump(mode="json")

    def list_runs(
        self,
        limit: int = 10,
        status: str | None = None,
        agent_name: str | None = None,
    ) -> list[dict[str, Any]]:
        statement = select(Run)
        if status is not None:
            statement = statement.where(Run.status == status)
        if agent_name is not None:
            statement = statement.where(Run.agent_name == agent_name)
        statement = statement.order_by(desc(Run.started_at)).limit(limit)

        with self._session_factory() as session:
            runs = list(session.exec(statement))

        return [self._run_dict(run) for run in runs]

    def _get_run_model(self, session: Session, run_id: str) -> Run:
        run = session.exec(select(Run).where(Run.run_id == run_id)).first()
        if run is None:
            raise ValueError(f"Run not found: {run_id}")
        return run

    def _run_record(self, run: Run) -> RunRecord:
        return RunRecord(
            run_id=run.run_id,
            agent_name=run.agent_name,
            task=run.task,
            status=run.status,
            user_id=run.user_id,
            session_id=run.session_id,
            metadata=self._load_json(run.metadata_json),
            started_at=run.started_at,
            finished_at=run.finished_at,
        )

    def _event_record(self, event: Event) -> EventRecord:
        return EventRecord(
            event_id=event.event_id,
            run_id=event.run_id,
            sequence=event.sequence,
            event_type=event.event_type,
            step_index=event.step_index,
            severity=event.severity,
            payload=self._load_json(event.payload_json) or {},
            created_at=event.created_at,
        )

    def _run_dict(self, run: Run) -> dict[str, Any]:
        return self._run_record(run).model_dump(mode="json")

    def _event_dict(self, event: Event) -> dict[str, Any]:
        return self._event_record(event).model_dump(mode="json")

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _dump_json(value: dict[str, Any] | None) -> str | None:
        if value is None:
            return None
        return json.dumps(value, sort_keys=True)

    @staticmethod
    def _load_json(value: str | None) -> dict[str, Any] | None:
        if value is None:
            return None
        return json.loads(value)
