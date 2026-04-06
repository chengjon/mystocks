from __future__ import annotations

import json
import subprocess

import pytest

from scripts.runtime import graphiti_smoke_common


def test_run_coordctl_json_uses_external_command_prefix(monkeypatch) -> None:
    monkeypatch.setenv("GRAPHITI_SMOKE_COMMAND", "/tmp/fake-cmd")
    monkeypatch.setattr(
        graphiti_smoke_common.subprocess,
        "run",
        lambda *_args, **_kwargs: type(
            "CompletedProcess",
            (),
            {"stdout": '{"ok": true}', "stderr": "", "returncode": 0},
        )(),
    )

    payload = graphiti_smoke_common.run_coordctl_json(["graphiti", "search"], coordctl_main=lambda _argv: 0)

    assert payload == {"ok": True}


def test_run_coordctl_json_wraps_external_failure(monkeypatch) -> None:
    monkeypatch.setenv("GRAPHITI_SMOKE_COMMAND", "/tmp/fake-cmd")

    def _raise(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, ["fake", "cmd"], output="out", stderr="boom")

    monkeypatch.setattr(graphiti_smoke_common.subprocess, "run", _raise)

    with pytest.raises(RuntimeError, match="external smoke command failed"):
        graphiti_smoke_common.run_coordctl_json(["graphiti", "search"], coordctl_main=lambda _argv: 0)


def test_run_coordctl_json_uses_coordctl_main_when_no_external_prefix(monkeypatch) -> None:
    monkeypatch.delenv("GRAPHITI_SMOKE_COMMAND", raising=False)

    def _coordctl_main(_argv: list[str]) -> int:
        print(json.dumps({"ok": True}))
        return 0

    payload = graphiti_smoke_common.run_coordctl_json(["graphiti", "search"], coordctl_main=_coordctl_main)

    assert payload == {"ok": True}
