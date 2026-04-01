from __future__ import annotations

import io
import os
import shlex
import subprocess
from contextlib import redirect_stdout
from typing import Callable

from src.utils.cli_error_output import build_external_command_runtime_error, parse_json_command_output


def run_coordctl_json(argv: list[str], *, coordctl_main: Callable[[list[str]], int]) -> dict[str, object]:
    command_prefix = os.getenv("GRAPHITI_SMOKE_COMMAND")
    if command_prefix:
        command = [*shlex.split(command_prefix), *argv]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise build_external_command_runtime_error(argv, exc) from exc
        payload = completed.stdout.strip()
        return parse_json_command_output(payload, argv=argv, source="external smoke command")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = coordctl_main(argv)
    if exit_code != 0:
        raise RuntimeError(f"coordctl failed for argv={argv!r}")
    payload = buffer.getvalue().strip()
    return parse_json_command_output(payload, argv=argv, source="coordctl")
