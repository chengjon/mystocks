from __future__ import annotations

import json


def build_cli_error_payload(error: Exception, *, audit_id: str | None = None) -> dict[str, str]:
    payload = {
        "error_code": error.__class__.__name__,
        "message": str(error),
    }
    if audit_id:
        payload["audit_id"] = audit_id
    return payload


def render_cli_error_json(error: Exception, *, audit_id: str | None = None) -> str:
    return json.dumps(build_cli_error_payload(error, audit_id=audit_id), ensure_ascii=False, indent=2, sort_keys=True)


def print_cli_error(error: Exception, *, audit_id: str | None = None) -> None:
    print(render_cli_error_json(error, audit_id=audit_id))


def build_external_command_runtime_error(argv: list[str], error: Exception, *, prefix: str = "external smoke command failed") -> RuntimeError:
    detail = getattr(error, "stderr", None) or str(error)
    return RuntimeError(f"{prefix} for argv={argv!r}: {detail}")


def parse_json_command_output(payload: str, *, argv: list[str], source: str) -> dict[str, object]:
    if not payload:
        raise RuntimeError(f"{source} returned no output for argv={argv!r}")
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{source} returned invalid JSON for argv={argv!r}") from exc
