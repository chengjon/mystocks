from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_FORBIDDEN_PACKAGES = [
    "TA-Lib",
    "pytest",
    "pytest-asyncio",
    "playwright",
    "pytest-playwright",
    "openpyxl",
    "xlwings",
]


def _extract_filter_pattern(dockerfile_text: str) -> str:
    match = re.search(r"grep\s+-E[v]?\s+'([^']+)'\s+requirements\.txt", dockerfile_text)
    if not match:
        raise ValueError("Could not locate runtime dependency filter pattern in Dockerfile")
    return match.group(1)


def _requirement_names(requirements_text: str) -> set[str]:
    names: set[str] = set()
    for raw_line in requirements_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~\[]", line, maxsplit=1)[0].strip()
        if name:
            names.add(name)
    return names


def validate_runtime_dependencies(
    dockerfile_path: Path,
    requirements_path: Path,
    forbidden_packages: list[str],
) -> dict[str, object]:
    dockerfile_text = dockerfile_path.read_text(encoding="utf-8")
    requirements_text = requirements_path.read_text(encoding="utf-8")
    filter_pattern = _extract_filter_pattern(dockerfile_text)
    requirements = _requirement_names(requirements_text)
    regex = re.compile(filter_pattern)

    present_forbidden = [package for package in forbidden_packages if package in requirements]
    filtered_forbidden = [package for package in present_forbidden if regex.search(f"{package}==0")]
    missing_filtered = [package for package in present_forbidden if package not in filtered_forbidden]

    return {
        "pass": not missing_filtered,
        "dockerfile": str(dockerfile_path.resolve()),
        "requirements_file": str(requirements_path.resolve()),
        "docker_filter_pattern": filter_pattern,
        "forbidden_packages_present": present_forbidden,
        "filtered_forbidden_packages": filtered_forbidden,
        "missing_filtered_packages": missing_filtered,
        "violations": [
            f"Forbidden runtime package is not filtered from Docker image: {package}" for package in missing_filtered
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate forbidden test/heavy packages do not flow into backend runtime image.")
    parser.add_argument("--dockerfile", required=True, type=Path)
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--forbidden-package", action="append", dest="forbidden_packages")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = validate_runtime_dependencies(
        dockerfile_path=args.dockerfile.resolve(),
        requirements_path=args.requirements.resolve(),
        forbidden_packages=args.forbidden_packages or DEFAULT_FORBIDDEN_PACKAGES,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if payload["pass"]:
        print(f"[backend-runtime-deps] pass: {args.output}")
        return

    print(f"[backend-runtime-deps] fail: {args.output}")
    for violation in payload["violations"]:
        print(f"  - {violation}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
