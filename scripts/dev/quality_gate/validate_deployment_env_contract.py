from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_ENV_EXAMPLE_KEYS = {
    "POSTGRESQL_HOST",
    "POSTGRESQL_PORT",
    "POSTGRESQL_USER",
    "POSTGRESQL_PASSWORD",
    "POSTGRESQL_DATABASE",
    "POSTGRES_PASSWORD",
    "TDENGINE_HOST",
    "TDENGINE_PORT",
    "TDENGINE_USER",
    "TDENGINE_PASSWORD",
    "TDENGINE_DATABASE",
    "JWT_SECRET_KEY",
    "CORS_ORIGINS",
    "FRONTEND_PORT",
    "FRONTEND_BACKUP_PORT",
    "BACKEND_PORT",
    "BACKEND_BACKUP_PORT",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_env_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def _extract_require_env_calls(text: str) -> set[str]:
    return set(re.findall(r'requireEnv\("([A-Z0-9_]+)"\)', text))


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


def validate_deployment_env_contract(
    env_example_path: Path,
    backend_ecosystem_path: Path,
    frontend_ecosystem_path: Path,
) -> dict[str, Any]:
    env_example_text = _read_text(env_example_path)
    backend_ecosystem_text = _read_text(backend_ecosystem_path)
    frontend_ecosystem_text = _read_text(frontend_ecosystem_path)

    env_keys = _extract_env_keys(env_example_text)
    backend_required = _extract_require_env_calls(backend_ecosystem_text)
    frontend_required = _extract_require_env_calls(frontend_ecosystem_text)

    checks: list[dict[str, Any]] = []
    violations: list[str] = []

    def expect(condition: bool, *, path: str, expected: Any, actual: Any, message: str) -> None:
        status = "pass" if condition else "fail"
        _add_check(checks, path=path, status=status, expected=expected, actual=actual, message=message)
        if not condition:
            violations.append(f"{path}: {message}")

    for key in sorted(REQUIRED_ENV_EXAMPLE_KEYS):
        expect(
            key in env_keys,
            path=f".env.example.{key}",
            expected="present",
            actual="present" if key in env_keys else "missing",
            message=f".env.example must document deployment/runtime key {key}",
        )

    for key in sorted(backend_required):
        expect(
            key in env_keys,
            path=f"backend_ecosystem.requireEnv.{key}",
            expected="documented in .env.example",
            actual="documented" if key in env_keys else "missing",
            message=f"Backend PM2 requireEnv key {key} must be documented in .env.example",
        )

    for key in sorted(frontend_required):
        expect(
            key in env_keys,
            path=f"frontend_ecosystem.requireEnv.{key}",
            expected="documented in .env.example",
            actual="documented" if key in env_keys else "missing",
            message=f"Frontend PM2 requireEnv key {key} must be documented in .env.example",
        )

    expect(
        "http://localhost:3020,http://localhost:3021" in env_example_text,
        path=".env.example.CORS_ORIGINS",
        expected="contains canonical and backup frontend localhost origins",
        actual="present" if "http://localhost:3020,http://localhost:3021" in env_example_text else "missing",
        message="CORS_ORIGINS must document canonical frontend 3020 and backup 3021 localhost origins",
    )

    return {
        "pass": not violations,
        "env_example_path": str(env_example_path.resolve()),
        "backend_ecosystem_path": str(backend_ecosystem_path.resolve()),
        "frontend_ecosystem_path": str(frontend_ecosystem_path.resolve()),
        "required_env_example_keys": sorted(REQUIRED_ENV_EXAMPLE_KEYS),
        "backend_required_env_keys": sorted(backend_required),
        "frontend_required_env_keys": sorted(frontend_required),
        "checks": checks,
        "violations": violations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deployment env contract across .env.example and PM2 ecosystem configs.")
    parser.add_argument("--env-example", required=True, type=Path)
    parser.add_argument("--backend-ecosystem", required=True, type=Path)
    parser.add_argument("--frontend-ecosystem", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = validate_deployment_env_contract(
        env_example_path=args.env_example.resolve(),
        backend_ecosystem_path=args.backend_ecosystem.resolve(),
        frontend_ecosystem_path=args.frontend_ecosystem.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if payload["pass"]:
        print(f"[deployment-env-contract] pass: {args.output}")
        return

    print(f"[deployment-env-contract] fail: {args.output}")
    for violation in payload["violations"]:
        print(f"  - {violation}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
