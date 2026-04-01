from __future__ import annotations

import json
import subprocess
import pytest

from src.utils.cli_error_output import (
    build_cli_error_payload,
    build_external_command_runtime_error,
    parse_json_command_output,
    print_cli_error,
    render_cli_error_json,
)


def test_build_cli_error_payload_includes_error_code_and_message() -> None:
    payload = build_cli_error_payload(RuntimeError("example failure"))

    assert payload == {
        "error_code": "RuntimeError",
        "message": "example failure",
    }


def test_build_cli_error_payload_can_include_audit_id() -> None:
    payload = build_cli_error_payload(ValueError("bad input"), audit_id="err-123")

    assert payload == {
        "audit_id": "err-123",
        "error_code": "ValueError",
        "message": "bad input",
    }


def test_render_cli_error_json_serializes_payload() -> None:
    rendered = render_cli_error_json(RuntimeError("boom"), audit_id="err-9")

    assert json.loads(rendered) == {
        "audit_id": "err-9",
        "error_code": "RuntimeError",
        "message": "boom",
    }


def test_build_external_command_runtime_error_uses_stderr_when_available() -> None:
    error = subprocess.CalledProcessError(1, ["fake", "cmd"], output="out", stderr="boom")

    runtime_error = build_external_command_runtime_error(["graphiti", "search"], error)

    assert "external smoke command failed" in str(runtime_error)
    assert "graphiti" in str(runtime_error)
    assert "boom" in str(runtime_error)


def test_parse_json_command_output_returns_payload_on_valid_json() -> None:
    payload = parse_json_command_output('{"ok": true}', argv=["graphiti", "search"], source="coordctl")

    assert payload == {"ok": True}


def test_parse_json_command_output_raises_on_empty_output() -> None:
    with pytest.raises(RuntimeError, match="coordctl returned no output"):
        parse_json_command_output("", argv=["graphiti", "search"], source="coordctl")


def test_parse_json_command_output_raises_on_invalid_json() -> None:
    with pytest.raises(RuntimeError, match="external smoke command returned invalid JSON"):
        parse_json_command_output("not-json", argv=["graphiti", "search"], source="external smoke command")


def test_print_cli_error_emits_rendered_json(capsys) -> None:
    print_cli_error(RuntimeError("boom"), audit_id="err-7")

    assert json.loads(capsys.readouterr().out) == {
        "audit_id": "err-7",
        "error_code": "RuntimeError",
        "message": "boom",
    }
