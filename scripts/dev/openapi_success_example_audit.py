#!/usr/bin/env python3
"""
Audit success-response OpenAPI examples against the generated FastAPI contract.

Rule:
- `application/json` success responses must provide `example` or `examples`.
- Non-JSON success responses (for example Prometheus `text/plain`) are reported
  separately and do not count as JSON contract debt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"

for candidate in (str(BACKEND_ROOT), str(PROJECT_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.main import app


JSON_MEDIA_TYPE = "application/json"


def collect_openapi_success_example_audit() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return JSON example gaps and non-JSON success-response observations."""
    schema = app.openapi()
    missing_json_examples: list[dict[str, Any]] = []
    non_json_success_responses: list[dict[str, Any]] = []

    for path, methods in schema.get("paths", {}).items():
        for method, operation in methods.items():
            responses = operation.get("responses", {})
            success_codes = sorted(code for code in responses if code.startswith("2"))

            for status_code in success_codes:
                if status_code == "204":
                    continue

                response_spec = responses[status_code]
                content = response_spec.get("content", {})
                if not content:
                    continue

                json_block = content.get(JSON_MEDIA_TYPE)
                if isinstance(json_block, dict):
                    if "example" not in json_block and "examples" not in json_block:
                        missing_json_examples.append(
                            {
                                "method": method.upper(),
                                "path": path,
                                "status_code": status_code,
                            }
                        )
                    continue

                non_json_success_responses.append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "status_code": status_code,
                        "media_types": sorted(content.keys()),
                    }
                )

    return missing_json_examples, non_json_success_responses


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit generated OpenAPI success-response examples."
    )
    parser.add_argument(
        "--show-non-json",
        action="store_true",
        help="Print non-JSON success responses that were excluded from JSON debt counting.",
    )
    args = parser.parse_args()

    missing_json_examples, non_json_success_responses = collect_openapi_success_example_audit()

    print(f"JSON_SUCCESS_MISSING_EXAMPLES {len(missing_json_examples)}")
    for item in missing_json_examples:
        print(f"{item['method']} {item['path']} {item['status_code']}")

    print(f"NON_JSON_SUCCESS_RESPONSES {len(non_json_success_responses)}")
    if args.show_non_json:
        for item in non_json_success_responses:
            media_types = ",".join(item["media_types"])
            print(f"{item['method']} {item['path']} {item['status_code']} [{media_types}]")

    return 1 if missing_json_examples else 0


if __name__ == "__main__":
    raise SystemExit(main())
