from __future__ import annotations

import threading
import time
from pathlib import Path

import uvicorn
from pymongo import MongoClient

from src.services.maestro.collab.registry import SQLiteCollaborationRegistry
from src.services.maestro.collab.runtime_registry import DualWriteCollaborationRegistry, MongoCollaborationRegistry

from .agent_runner import AgentRunner
from .config import ServiceConfig
from .orchestrator import SymphonyOrchestrator
from .status_api import create_status_app
from .tracker_factory import create_tracker_client
from .workflow_loader import load_workflow_definition


class RunnerThreadHandle:
    """Background worker handle for one dispatched issue."""

    def __init__(self, issue, attempt, runner: AgentRunner, orchestrator: SymphonyOrchestrator) -> None:
        self.issue = issue
        self.attempt = attempt
        self.runner = runner
        self.orchestrator = orchestrator
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.runner.stop()

    def _run(self) -> None:
        result = self.runner.run_attempt(
            self.issue,
            attempt=self.attempt,
            on_event=lambda event: self.orchestrator.record_event(self.issue.id, event),
        )
        self.orchestrator.record_worker_result(self.issue.id, result)
        reason = "normal" if result.status == "succeeded" else (result.error_code or "failed")
        self.orchestrator.on_worker_exit(self.issue.id, reason)


class SymphonyService:
    """Top-level Symphony runtime wiring."""

    def __init__(self, workflow_path: str | Path, port: int | None = None) -> None:
        self.workflow_path = Path(workflow_path)
        self.port = port
        self._workflow_mtime: float | None = None
        self._stop_event = threading.Event()
        self._server: uvicorn.Server | None = None
        self._server_thread: threading.Thread | None = None
        self.workflow_definition = load_workflow_definition(self.workflow_path)
        self.service_config = ServiceConfig.from_workflow_definition(self.workflow_definition)
        self.tracker_client = create_tracker_client(self.service_config.tracker)
        self.collab_registry = self._create_collab_registry(self.service_config)
        self.orchestrator = SymphonyOrchestrator(
            workflow_definition=self.workflow_definition,
            service_config=self.service_config,
            tracker_client=self.tracker_client,
            runner_factory=self._create_runner_handle,
            collab_registry=self.collab_registry,
        )
        self._workflow_mtime = self._get_workflow_mtime()

    def start(self) -> None:
        if self.port is not None:
            self._start_status_server(self.port)

    def run_forever(self) -> None:
        self.start()
        try:
            while not self._stop_event.is_set():
                self.reload_workflow_if_needed()
                self.orchestrator.tick_once()
                time.sleep(self.service_config.polling.interval_ms / 1000)
        finally:
            self.stop()

    def stop(self) -> None:
        self._stop_event.set()
        if self._server is not None:
            self._server.should_exit = True
        if self._server_thread is not None and self._server_thread.is_alive():
            self._server_thread.join(timeout=2)
        self.tracker_client.close()
        if self.collab_registry is not None:
            self.collab_registry.close()

    def reload_workflow_if_needed(self) -> None:
        current_mtime = self._get_workflow_mtime()
        if current_mtime is None or current_mtime == self._workflow_mtime:
            return

        workflow_definition = load_workflow_definition(self.workflow_path)
        service_config = ServiceConfig.from_workflow_definition(workflow_definition)
        self.workflow_definition = workflow_definition
        self.service_config = service_config
        self.tracker_client = create_tracker_client(service_config.tracker)
        self.collab_registry = self._create_collab_registry(service_config)
        self.orchestrator.workflow_definition = workflow_definition
        self.orchestrator.service_config = service_config
        self.orchestrator.collab_registry = self.collab_registry
        self.orchestrator.state.poll_interval_ms = service_config.polling.interval_ms
        self.orchestrator.state.max_concurrent_agents = service_config.agent.max_concurrent_agents
        self._workflow_mtime = current_mtime

    def _create_runner_handle(self, issue, attempt):
        runner = AgentRunner(
            workflow_definition=self.workflow_definition,
            service_config=self.service_config,
            tracker_client=self.tracker_client,
            collab_registry=self.collab_registry,
        )
        return RunnerThreadHandle(issue=issue, attempt=attempt, runner=runner, orchestrator=self.orchestrator)

    def _start_status_server(self, port: int) -> None:
        app = create_status_app(self.orchestrator)
        config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="info")
        self._server = uvicorn.Server(config)
        self._server_thread = threading.Thread(target=self._server.run, daemon=True)
        self._server_thread.start()

    def _get_workflow_mtime(self) -> float | None:
        if not self.workflow_path.exists():
            return None
        return self.workflow_path.stat().st_mtime

    @staticmethod
    def _create_collab_registry(service_config: ServiceConfig):
        tracker = service_config.tracker
        backend = service_config.runtime.collab_backend
        sqlite_registry = None
        if tracker.kind == "local" and tracker.sqlite_path is not None:
            sqlite_registry = SQLiteCollaborationRegistry(tracker.sqlite_path)

        if backend == "sqlite":
            return sqlite_registry

        mongo_database = MongoClient(service_config.runtime.collab_mongo_uri)[service_config.runtime.collab_mongo_db]
        mongo_registry = MongoCollaborationRegistry(mongo_database)

        if backend == "mongo":
            return mongo_registry
        if backend == "dual-write":
            if sqlite_registry is None:
                raise ValueError("dual-write collab backend requires a local sqlite tracker path")
            return DualWriteCollaborationRegistry(primary=mongo_registry, secondary=sqlite_registry)

        raise ValueError(f"Unsupported collab backend: {backend}")
