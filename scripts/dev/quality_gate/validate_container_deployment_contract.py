from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def _read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return payload


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _add_check(checks: list[dict[str, Any]], *, path: str, status: str, expected: Any, actual: Any, message: str) -> None:
    checks.append(
        {
            "path": path,
            "status": status,
            "expected": expected,
            "actual": actual,
            "message": message,
        }
    )


def validate_container_deployment_contract(
    compose_file: Path,
    smoke_script: Path,
    *,
    canonical_backend_port: int,
    canonical_frontend_port: int,
    backup_backend_port: int,
    backup_frontend_port: int,
) -> dict[str, Any]:
    compose = _read_yaml(compose_file)
    smoke_script_text = _read_text(smoke_script)
    services = compose.get("services") or {}
    if not isinstance(services, dict):
        raise ValueError("docker-compose services must be a mapping")

    checks: list[dict[str, Any]] = []
    violations: list[str] = []

    def expect(condition: bool, *, path: str, expected: Any, actual: Any, message: str) -> None:
        status = "pass" if condition else "fail"
        _add_check(checks, path=path, status=status, expected=expected, actual=actual, message=message)
        if not condition:
            violations.append(f"{path}: {message}")

    for service_name in ("backend", "frontend", "postgresql", "redis"):
        expect(
            service_name in services,
            path=f"services.{service_name}",
            expected="present",
            actual="present" if service_name in services else "missing",
            message=f"Service '{service_name}' must exist in docker-compose contract",
        )

    backend = services.get("backend") or {}
    frontend = services.get("frontend") or {}

    backend_ports = backend.get("ports") or []
    frontend_ports = frontend.get("ports") or []
    backend_env = backend.get("environment") or {}
    frontend_env = frontend.get("environment") or {}
    backend_depends_on = backend.get("depends_on") or []
    frontend_depends_on = frontend.get("depends_on") or []
    backend_command = backend.get("command") or ""
    frontend_command = frontend.get("command") or ""

    expect(
        f"${{BACKEND_PORT:-{canonical_backend_port}}}:${{BACKEND_PORT:-{canonical_backend_port}}}" in backend_ports,
        path="services.backend.ports",
        expected=f"${{BACKEND_PORT:-{canonical_backend_port}}}:${{BACKEND_PORT:-{canonical_backend_port}}}",
        actual=backend_ports,
        message="Backend compose port mapping must keep canonical env-driven default 8020",
    )
    expect(
        backend_env.get("BACKEND_PORT") == f"${{BACKEND_PORT:-{canonical_backend_port}}}",
        path="services.backend.environment.BACKEND_PORT",
        expected=f"${{BACKEND_PORT:-{canonical_backend_port}}}",
        actual=backend_env.get("BACKEND_PORT"),
        message="Backend compose env must retain canonical default port",
    )
    expect(
        f"${{FRONTEND_PORT:-{canonical_frontend_port}}}:${{FRONTEND_PORT:-{canonical_frontend_port}}}" in frontend_ports,
        path="services.frontend.ports",
        expected=f"${{FRONTEND_PORT:-{canonical_frontend_port}}}:${{FRONTEND_PORT:-{canonical_frontend_port}}}",
        actual=frontend_ports,
        message="Frontend compose port mapping must keep canonical env-driven default 3020",
    )
    expect(
        frontend_env.get("FRONTEND_PORT") == f"${{FRONTEND_PORT:-{canonical_frontend_port}}}",
        path="services.frontend.environment.FRONTEND_PORT",
        expected=f"${{FRONTEND_PORT:-{canonical_frontend_port}}}",
        actual=frontend_env.get("FRONTEND_PORT"),
        message="Frontend compose env must retain canonical default port",
    )
    expect(
        frontend_env.get("VITE_API_BASE_URL") == f"http://localhost:${{BACKEND_PORT:-{canonical_backend_port}}}",
        path="services.frontend.environment.VITE_API_BASE_URL",
        expected=f"http://localhost:${{BACKEND_PORT:-{canonical_backend_port}}}",
        actual=frontend_env.get("VITE_API_BASE_URL"),
        message="Frontend container must target canonical backend port by env contract",
    )
    expect(
        f"--port ${{BACKEND_PORT:-{canonical_backend_port}}}" in str(backend_command),
        path="services.backend.command",
        expected=f"--port ${{BACKEND_PORT:-{canonical_backend_port}}}",
        actual=str(backend_command),
        message="Backend container command must bind using canonical env-driven port",
    )
    expect(
        f"--port ${{FRONTEND_PORT:-{canonical_frontend_port}}}" in str(frontend_command),
        path="services.frontend.command",
        expected=f"--port ${{FRONTEND_PORT:-{canonical_frontend_port}}}",
        actual=str(frontend_command),
        message="Frontend container command must bind using canonical env-driven port",
    )
    expect(
        set(backend_depends_on) >= {"postgresql", "redis"},
        path="services.backend.depends_on",
        expected=["postgresql", "redis"],
        actual=backend_depends_on,
        message="Backend container must depend on postgresql and redis",
    )
    expect(
        "backend" in set(frontend_depends_on),
        path="services.frontend.depends_on",
        expected=["backend"],
        actual=frontend_depends_on,
        message="Frontend container must depend on backend",
    )

    expect(
        f'BACKEND_PORT="${{BACKEND_PORT:-{backup_backend_port}}}"' in smoke_script_text,
        path="smoke_script.backend_port_default",
        expected=backup_backend_port,
        actual="present" if f'BACKEND_PORT="${{BACKEND_PORT:-{backup_backend_port}}}"' in smoke_script_text else "missing",
        message="Container smoke script must default backend to backup port 8021",
    )
    expect(
        f'FRONTEND_PORT="${{FRONTEND_PORT:-{backup_frontend_port}}}"' in smoke_script_text,
        path="smoke_script.frontend_port_default",
        expected=backup_frontend_port,
        actual="present" if f'FRONTEND_PORT="${{FRONTEND_PORT:-{backup_frontend_port}}}"' in smoke_script_text else "missing",
        message="Container smoke script must default frontend to backup port 3021",
    )
    expect(
        backup_backend_port != canonical_backend_port and backup_frontend_port != canonical_frontend_port,
        path="smoke_script.port_role_separation",
        expected={
            "canonical": {"backend": canonical_backend_port, "frontend": canonical_frontend_port},
            "backup_smoke": {"backend": backup_backend_port, "frontend": backup_frontend_port},
        },
        actual={
            "canonical": {"backend": canonical_backend_port, "frontend": canonical_frontend_port},
            "backup_smoke": {"backend": backup_backend_port, "frontend": backup_frontend_port},
        },
        message="Backup smoke ports must stay distinct from canonical PM2 runtime ports",
    )

    return {
        "pass": not violations,
        "compose_file": str(compose_file.resolve()),
        "smoke_script": str(smoke_script.resolve()),
        "canonical_ports": {"backend": canonical_backend_port, "frontend": canonical_frontend_port},
        "backup_smoke_ports": {"backend": backup_backend_port, "frontend": backup_frontend_port},
        "checks": checks,
        "violations": violations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate docker compose and smoke port role deployment contract.")
    parser.add_argument("--compose-file", required=True, type=Path)
    parser.add_argument("--smoke-script", required=True, type=Path)
    parser.add_argument("--canonical-backend-port", type=int, default=8020)
    parser.add_argument("--canonical-frontend-port", type=int, default=3020)
    parser.add_argument("--backup-backend-port", type=int, default=8021)
    parser.add_argument("--backup-frontend-port", type=int, default=3021)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = validate_container_deployment_contract(
        compose_file=args.compose_file.resolve(),
        smoke_script=args.smoke_script.resolve(),
        canonical_backend_port=args.canonical_backend_port,
        canonical_frontend_port=args.canonical_frontend_port,
        backup_backend_port=args.backup_backend_port,
        backup_frontend_port=args.backup_frontend_port,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if payload["pass"]:
        print(f"[container-deployment-contract] pass: {args.output}")
        return

    print(f"[container-deployment-contract] fail: {args.output}")
    for violation in payload["violations"]:
        print(f"  - {violation}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
