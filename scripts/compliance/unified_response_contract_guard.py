from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any


SCOPE_ROOT = "web/backend/app/api"
RULE_ID = "unified-response-contract"
HTTP_ROUTE_DECORATORS = {"get", "post", "put", "delete", "patch", "options", "head", "api_route"}
ALLOWED_RESPONSE_MODELS = ("UnifiedResponse", "UnifiedPaginatedResponse")
RAW_RESPONSE_TYPES = (
    "EventSourceResponse",
    "StreamingResponse",
    "FileResponse",
    "PlainTextResponse",
    "HTMLResponse",
    "RedirectResponse",
    "Response",
)
NO_CONTENT_STATUS_MARKERS = {"204", "status.HTTP_204_NO_CONTENT", "HTTPStatus.NO_CONTENT"}


def normalize_input_path(raw_path: str) -> str:
    value = raw_path.strip().replace("\\", "/")
    if not value:
        return ""

    marker_index = value.find(SCOPE_ROOT)
    if marker_index >= 0:
        value = value[marker_index:]
    elif value.startswith("./"):
        value = value[2:]

    return Path(value).as_posix().strip("/")


def is_scoped_path(path_value: str) -> bool:
    return (
        path_value.endswith(".py")
        and (path_value == SCOPE_ROOT or path_value.startswith(f"{SCOPE_ROOT}/"))
        and not path_value.endswith("/__init__.py")
    )


def discover_candidate_files(project_root: Path, scoped_paths: list[str]) -> list[Path]:
    candidates: list[Path] = []
    for relative_path in scoped_paths:
        if not is_scoped_path(relative_path):
            continue
        file_path = project_root / relative_path
        if file_path.is_file():
            candidates.append(file_path)
    return sorted(set(candidates))


def route_decorators(node: ast.AST) -> list[ast.Call]:
    decorators: list[ast.Call] = []
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return decorators

    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr in HTTP_ROUTE_DECORATORS
        ):
            decorators.append(decorator)
    return decorators


def expression_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def keyword_node(decorator: ast.Call, keyword_name: str) -> ast.AST | None:
    for keyword in decorator.keywords:
        if keyword.arg == keyword_name:
            return keyword.value
    return None


def expression_references_name(expression: str, name: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(name)}(?!\w)", expression))


def expression_references_any(expression: str, names: tuple[str, ...]) -> bool:
    return any(expression_references_name(expression, name) for name in names)


def has_unified_response_model(decorators: list[ast.Call]) -> tuple[bool, str]:
    for decorator in decorators:
        response_model_expression = expression_text(keyword_node(decorator, "response_model"))
        if response_model_expression and expression_references_any(response_model_expression, ALLOWED_RESPONSE_MODELS):
            return True, response_model_expression
    return False, ""


def is_no_content_status(decorators: list[ast.Call]) -> bool:
    for decorator in decorators:
        status_expression = expression_text(keyword_node(decorator, "status_code"))
        if not status_expression:
            continue
        if status_expression in NO_CONTENT_STATUS_MARKERS:
            return True
        if status_expression.isdigit() and int(status_expression) == 204:
            return True
    return False


def raw_response_reason(function_node: ast.FunctionDef | ast.AsyncFunctionDef, decorators: list[ast.Call]) -> str | None:
    if is_no_content_status(decorators):
        return "204 no-content endpoint"

    for decorator in decorators:
        response_class_expression = expression_text(keyword_node(decorator, "response_class"))
        if response_class_expression and expression_references_any(response_class_expression, RAW_RESPONSE_TYPES):
            return f"raw response_class={response_class_expression}"

    return_expression = expression_text(function_node.returns)
    if return_expression and expression_references_any(return_expression, RAW_RESPONSE_TYPES):
        return f"raw return annotation={return_expression}"

    for node in ast.walk(function_node):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            callee_expression = expression_text(node.value.func)
            if callee_expression and expression_references_any(callee_expression, RAW_RESPONSE_TYPES):
                return f"raw return call={callee_expression}"

    return None


def endpoint_route_label(decorators: list[ast.Call]) -> str:
    routes: list[str] = []
    for decorator in decorators:
        method = decorator.func.attr.upper()
        if decorator.func.attr == "api_route":
            methods_expression = expression_text(keyword_node(decorator, "methods")) or "API_ROUTE"
            method = methods_expression

        route_path = ""
        if decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
            route_path = decorator.args[0].value

        routes.append(f"{method} {route_path}".strip())
    return ", ".join(routes)


def evaluate_file(path_value: str, raw_path: str, project_root: Path) -> dict[str, Any]:
    file_path = project_root / normalize_input_path(raw_path)
    if not file_path.exists():
        return {
            "path": path_value,
            "passed": False,
            "message": "Target file does not exist",
            "mode": "missing",
            "errors": [
                {
                    "path": path_value,
                    "rule_id": RULE_ID,
                    "message": "Target file does not exist",
                }
            ],
            "checked_routes": 0,
            "results": [],
        }

    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return {
            "path": path_value,
            "passed": False,
            "message": f"Failed to parse Python file: {exc.msg}",
            "mode": "parse-error",
            "errors": [
                {
                    "path": path_value,
                    "rule_id": "python-parse-error",
                    "message": f"Failed to parse Python file: {exc.msg}",
                }
            ],
            "checked_routes": 0,
            "results": [],
        }

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for node in tree.body:
        decorators = route_decorators(node)
        if not decorators:
            continue

        route_label = endpoint_route_label(decorators)
        exempt_reason = raw_response_reason(node, decorators)
        has_unified, response_model_expression = has_unified_response_model(decorators)

        if exempt_reason:
            results.append(
                {
                    "path": path_value,
                    "endpoint": node.name,
                    "route": route_label,
                    "passed": True,
                    "mode": "raw-exempt",
                    "message": f"Exempt raw endpoint: {exempt_reason}",
                }
            )
            continue

        if has_unified:
            results.append(
                {
                    "path": path_value,
                    "endpoint": node.name,
                    "route": route_label,
                    "passed": True,
                    "mode": "unified-response-model",
                    "message": f"Declares response_model={response_model_expression}",
                }
            )
            continue

        response_model_expression = ""
        for decorator in decorators:
            response_model_expression = expression_text(keyword_node(decorator, "response_model"))
            if response_model_expression:
                break

        message = "HTTP route must declare response_model=UnifiedResponse[...] or UnifiedPaginatedResponse[...]"
        if response_model_expression:
            message = f"{message}; found response_model={response_model_expression}"

        result = {
            "path": path_value,
            "endpoint": node.name,
            "route": route_label,
            "passed": False,
            "mode": "missing-unified-response-model",
            "message": message,
        }
        results.append(result)
        errors.append(
            {
                "path": path_value,
                "endpoint": node.name,
                "route": route_label,
                "rule_id": RULE_ID,
                "message": message,
            }
        )

    return {
        "path": path_value,
        "passed": not errors,
        "message": "All HTTP routes declare UnifiedResponse contract" if not errors else "Missing UnifiedResponse contract",
        "mode": "ok" if not errors else "has-violations",
        "errors": errors,
        "checked_routes": len(results),
        "results": results,
    }


def build_report(project_root: Path, paths: list[str] | None = None) -> dict[str, Any]:
    normalized_inputs: list[str] = []
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for raw_path in paths or []:
        normalized = normalize_input_path(raw_path)
        if not normalized or not is_scoped_path(normalized):
            continue
        normalized_inputs.append(normalized)

    candidate_files = discover_candidate_files(project_root, normalized_inputs)
    checked_routes = 0

    for file_path in candidate_files:
        relative_path = file_path.relative_to(project_root).as_posix()
        file_result = evaluate_file(relative_path, relative_path, project_root)
        checked_routes += file_result["checked_routes"]
        results.extend(file_result["results"])
        errors.extend(file_result["errors"])

    return {
        "project_root": str(project_root),
        "scope_root": SCOPE_ROOT,
        "paths": sorted(set(normalized_inputs)),
        "checked_files": len(candidate_files),
        "checked_routes": checked_routes,
        "results": results,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checked_files": len(candidate_files),
            "checked_routes": checked_routes,
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("UnifiedResponse Contract Guard")
    print("==============================")
    print(f"checked_files: {report['checked_files']}")
    print(f"checked_routes: {report['checked_routes']}")
    print(f"errors: {report['summary']['errors']}")

    if report["results"]:
        print("\nRoute results:")
        for item in report["results"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(f"  - {item['path']}::{item['endpoint']}: {status} — {item['message']}")

    if not report["results"]:
        print("\nNo changed backend API Python files detected for UnifiedResponse contract guard.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate UnifiedResponse response_model contract for changed backend API routes")
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    merged_paths = [*(args.path or []), *args.filenames]
    report = build_report(Path(args.root_dir).resolve(), merged_paths)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
