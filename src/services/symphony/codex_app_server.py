from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from itertools import count
from pathlib import Path
from typing import Any, Callable

from .dynamic_tools import DynamicToolDefinition, DynamicToolResult
from .models import CodexTurnResult, LiveCodexSession

EventCallback = Callable[[dict[str, Any]], None]


class CodexAppServerClient:
    """Minimal JSON-line Codex app-server client for Symphony."""

    def __init__(
        self,
        command: str,
        read_timeout_ms: int = 5000,
        turn_timeout_ms: int = 3600000,
        dynamic_tools: dict[str, DynamicToolDefinition] | None = None,
    ) -> None:
        self.command = command
        self.read_timeout_ms = read_timeout_ms
        self.turn_timeout_ms = turn_timeout_ms
        self.dynamic_tools = dynamic_tools or {}
        self._request_ids = count(1)
        self._response_queues: dict[str, queue.Queue[dict[str, Any]]] = {}
        self._event_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._reader_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None

    def start_session(
        self,
        workspace_path: Path,
        approval_policy: Any = None,
        thread_sandbox: Any = None,
        on_event: EventCallback | None = None,
    ) -> LiveCodexSession:
        process = subprocess.Popen(
            ["bash", "-lc", self.command],
            cwd=workspace_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None

        self._reader_thread = threading.Thread(target=self._read_stdout, args=(process.stdout,), daemon=True)
        self._stderr_thread = threading.Thread(target=self._drain_stderr, args=(process.stderr, on_event), daemon=True)
        self._reader_thread.start()
        self._stderr_thread.start()

        self._send_request(
            process,
            "initialize",
            {"clientInfo": {"name": "mystocks-symphony", "version": "0.1.0"}, "capabilities": {}},
        )
        self._send_notification(process, "initialized", {})
        thread_start_params: dict[str, Any] = {
            "approvalPolicy": approval_policy,
            "sandbox": thread_sandbox,
            "cwd": str(workspace_path),
        }
        if self.dynamic_tools:
            thread_start_params["config"] = {
                "dynamic_tools": [tool.to_payload() for tool in self.dynamic_tools.values()],
            }
        thread_response = self._send_request(process, "thread/start", thread_start_params)
        thread_id = (((thread_response.get("result") or {}).get("thread") or {}).get("id")) or ""
        session = LiveCodexSession(
            process=process,
            workspace_path=workspace_path,
            thread_id=thread_id,
            pid=process.pid,
        )
        self._emit(
            on_event,
            {
                "event": "session_started",
                "thread_id": thread_id,
                "codex_app_server_pid": process.pid,
                "timestamp": time.time(),
            },
        )
        return session

    def run_turn(
        self,
        session: LiveCodexSession,
        prompt: str,
        title: str,
        approval_policy: Any = None,
        sandbox_policy: Any = None,
        on_event: EventCallback | None = None,
    ) -> CodexTurnResult:
        turn_response = self._send_request(
            session.process,
            "turn/start",
            {
                "threadId": session.thread_id,
                "input": [{"type": "text", "text": prompt}],
                "cwd": str(session.workspace_path),
                "title": title,
                "approvalPolicy": approval_policy,
                "sandboxPolicy": sandbox_policy,
            },
        )
        turn_id = (((turn_response.get("result") or {}).get("turn") or {}).get("id")) or ""
        session.last_turn_id = turn_id
        deadline = time.time() + (self.turn_timeout_ms / 1000)

        while time.time() < deadline:
            if session.process.poll() is not None:
                return CodexTurnResult(
                    status="failed",
                    turn_id=turn_id,
                    session_id=f"{session.thread_id}-{turn_id}",
                    input_tokens=session.input_tokens,
                    output_tokens=session.output_tokens,
                    total_tokens=session.total_tokens,
                    error_code="port_exit",
                )

            try:
                message = self._event_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if "method" in message and "id" in message and "result" not in message and "error" not in message:
                self._handle_server_request(session, message, on_event)
                continue

            method = message.get("method")
            params = message.get("params", {})
            event_type = params.get("type") or method

            if method == "thread/tokenUsage/updated":
                self._update_usage(session, params)
                self._emit(
                    on_event,
                    {
                        "event": "token_usage_updated",
                        "thread_id": params.get("threadId"),
                        "turn_id": params.get("turnId"),
                        "input_tokens": session.input_tokens,
                        "output_tokens": session.output_tokens,
                        "total_tokens": session.total_tokens,
                        "timestamp": time.time(),
                    },
                )
                continue

            if event_type in {"turn/completed", "turn_completed"}:
                self._emit(
                    on_event,
                    {"event": "turn_completed", "turn_id": turn_id, "session_id": f"{session.thread_id}-{turn_id}"},
                )
                return CodexTurnResult(
                    status="completed",
                    turn_id=turn_id,
                    session_id=f"{session.thread_id}-{turn_id}",
                    input_tokens=session.input_tokens,
                    output_tokens=session.output_tokens,
                    total_tokens=session.total_tokens,
                )

            if event_type in {"turn/failed", "turn_failed"}:
                return CodexTurnResult(
                    status="failed",
                    turn_id=turn_id,
                    session_id=f"{session.thread_id}-{turn_id}",
                    input_tokens=session.input_tokens,
                    output_tokens=session.output_tokens,
                    total_tokens=session.total_tokens,
                    error_code="turn_failed",
                )

            if event_type in {"turn/cancelled", "turn_cancelled"}:
                return CodexTurnResult(
                    status="cancelled",
                    turn_id=turn_id,
                    session_id=f"{session.thread_id}-{turn_id}",
                    input_tokens=session.input_tokens,
                    output_tokens=session.output_tokens,
                    total_tokens=session.total_tokens,
                    error_code="turn_cancelled",
                )

            if event_type == "request_user_input" or "requestUserInput" in str(method):
                self._emit(on_event, {"event": "turn_input_required", "turn_id": turn_id})
                return CodexTurnResult(
                    status="input_required",
                    turn_id=turn_id,
                    session_id=f"{session.thread_id}-{turn_id}",
                    input_tokens=session.input_tokens,
                    output_tokens=session.output_tokens,
                    total_tokens=session.total_tokens,
                    error_code="turn_input_required",
                )

            self._emit(
                on_event,
                {
                    "event": "notification",
                    "method": method,
                    "type": event_type,
                    "timestamp": time.time(),
                },
            )

        return CodexTurnResult(
            status="failed",
            turn_id=turn_id,
            session_id=f"{session.thread_id}-{turn_id}",
            input_tokens=session.input_tokens,
            output_tokens=session.output_tokens,
            total_tokens=session.total_tokens,
            error_code="turn_timeout",
        )

    def stop_session(self, session: LiveCodexSession) -> None:
        process = session.process
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

    def _read_stdout(self, stdout) -> None:
        for raw_line in stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._event_queue.put({"method": "malformed", "params": {"line": line}})
                continue

            response_id = message.get("id")
            if response_id is not None and "method" not in message and (("result" in message) or ("error" in message)):
                response_queue = self._response_queues.get(str(response_id))
                if response_queue is not None:
                    response_queue.put(message)
                    continue

            self._event_queue.put(message)

    def _drain_stderr(self, stderr, on_event: EventCallback | None = None) -> None:
        for raw_line in stderr:
            line = raw_line.strip()
            if not line:
                continue
            self._emit(on_event, {"event": "stderr", "message": line, "timestamp": time.time()})

    def _send_request(self, process: subprocess.Popen[str], method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = str(next(self._request_ids))
        response_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)
        self._response_queues[request_id] = response_queue
        self._write_message(process, {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        try:
            return response_queue.get(timeout=self.read_timeout_ms / 1000)
        finally:
            self._response_queues.pop(request_id, None)

    def _send_notification(self, process: subprocess.Popen[str], method: str, params: dict[str, Any]) -> None:
        self._write_message(process, {"jsonrpc": "2.0", "method": method, "params": params})

    @staticmethod
    def _write_message(process: subprocess.Popen[str], message: dict[str, Any]) -> None:
        assert process.stdin is not None
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def _handle_server_request(
        self, session: LiveCodexSession, message: dict[str, Any], on_event: EventCallback | None
    ) -> None:
        method = str(message.get("method", ""))
        params = message.get("params", {})
        request_id = str(message.get("id"))
        event_type = params.get("type")

        if event_type == "exec_approval_request" or "approval" in method:
            self._write_message(
                session.process,
                {"jsonrpc": "2.0", "id": request_id, "result": {"decision": "approved_for_session"}},
            )
            self._emit(on_event, {"event": "approval_auto_approved", "request_id": request_id})
            return

        if event_type == "dynamic_tool_call_request" or "dynamic_tool" in method:
            tool_name = str(params.get("tool", "")).strip()
            tool = self.dynamic_tools.get(tool_name)
            if tool is None:
                self._write_message(
                    session.process,
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": DynamicToolResult.json(
                            {
                                "error": {
                                    "code": "unsupported_tool_call",
                                    "message": f"Unsupported dynamic tool: {tool_name or 'unknown'}",
                                }
                            },
                            success=False,
                            error="unsupported_tool_call",
                        ).to_protocol_result(),
                    },
                )
                self._emit(
                    on_event,
                    {"event": "unsupported_tool_call", "request_id": request_id, "tool_name": tool_name},
                )
                return

            raw_arguments = params.get("arguments")
            arguments = raw_arguments if isinstance(raw_arguments, dict) else {}
            try:
                result = tool.handler(arguments)
            except Exception as exc:
                result = DynamicToolResult.json(
                    {"error": {"code": "dynamic_tool_execution_failed", "message": str(exc)}},
                    success=False,
                    error="dynamic_tool_execution_failed",
                )
            self._write_message(
                session.process, {"jsonrpc": "2.0", "id": request_id, "result": result.to_protocol_result()}
            )
            self._emit(
                on_event,
                {
                    "event": "dynamic_tool_call_completed",
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "success": result.success,
                },
            )
            return

        self._write_message(session.process, {"jsonrpc": "2.0", "id": request_id, "result": {"success": False}})

    @staticmethod
    def _update_usage(session: LiveCodexSession, params: dict[str, Any]) -> None:
        total = (params.get("tokenUsage") or {}).get("total", {})
        session.input_tokens = int(total.get("inputTokens", session.input_tokens))
        session.output_tokens = int(total.get("outputTokens", session.output_tokens))
        session.total_tokens = int(total.get("totalTokens", session.total_tokens))

    @staticmethod
    def _emit(callback: EventCallback | None, payload: dict[str, Any]) -> None:
        if callback is not None:
            callback(payload)
