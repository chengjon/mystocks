#!/usr/bin/env python3
"""Validate Prometheus rule files only reference metrics present in runtime snapshots."""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TOKEN_RE = re.compile(r"\b[a-zA-Z_:][a-zA-Z0-9_:]*\b")
METRIC_LINE_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{.*\})?\s+[-+0-9.eE]+(?:\s+\d+)?$")
RANGE_SELECTOR_RE = re.compile(r"\[[^\]]+\]")
STRING_RE = re.compile(r'"(?:\\.|[^"])*"')
GROUPING_CLAUSE_RE = re.compile(r"\b(?:by|without|on|ignoring|group_left|group_right)\s*\([^)]*\)")

PROMQL_KEYWORDS = {
    "and",
    "bool",
    "by",
    "group_left",
    "group_right",
    "ignoring",
    "offset",
    "on",
    "or",
    "unless",
    "without",
}

PROMQL_FUNCTIONS = {
    "abs",
    "absent",
    "avg",
    "avg_over_time",
    "ceil",
    "clamp_max",
    "clamp_min",
    "count",
    "count_over_time",
    "delta",
    "deriv",
    "floor",
    "histogram_quantile",
    "holt_winters",
    "idelta",
    "increase",
    "irate",
    "label_join",
    "label_replace",
    "max",
    "max_over_time",
    "min",
    "min_over_time",
    "predict_linear",
    "quantile_over_time",
    "rate",
    "resets",
    "round",
    "scalar",
    "sort",
    "sort_desc",
    "stddev",
    "stddev_over_time",
    "stdvar",
    "stdvar_over_time",
    "sum",
    "sum_over_time",
    "time",
    "timestamp",
    "vector",
}


def _read_metrics_names(path: Path) -> set[str]:
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = METRIC_LINE_RE.match(line)
        if match:
            names.add(match.group(1))
    return names


def _extract_declared_metrics_from_python(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    metric_names: set[str] = set()
    metric_factories = {"Counter", "Gauge", "Histogram", "Info", "Summary"}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name: str | None = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name not in metric_factories or not node.args:
            continue

        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            metric_names.add(first_arg.value)

    return metric_names


def _strip_label_matchers(expression: str) -> str:
    expression = STRING_RE.sub('""', expression)
    sanitized: list[str] = []
    depth = 0
    for char in expression:
        if char == "{":
            depth += 1
            sanitized.append(char)
            continue
        if char == "}":
            depth = max(depth - 1, 0)
            sanitized.append(char)
            continue
        if depth > 0:
            continue
        sanitized.append(char)
    stripped = RANGE_SELECTOR_RE.sub("", "".join(sanitized))
    return GROUPING_CLAUSE_RE.sub("", stripped)


def extract_metric_references(expression: str) -> list[str]:
    sanitized = _strip_label_matchers(expression)
    references: list[str] = []
    for token in TOKEN_RE.findall(sanitized):
        if token in PROMQL_KEYWORDS or token in PROMQL_FUNCTIONS:
            continue
        if "_" not in token and ":" not in token:
            continue
        references.append(token)
    return sorted(set(references))


def _iter_rule_entries(path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for group in payload.get("groups", []) or []:
        group_name = group.get("name", "unnamed-group")
        for rule in group.get("rules", []) or []:
            expression = rule.get("expr")
            if not expression:
                continue
            entries.append(
                {
                    "rule_file": str(path.resolve()),
                    "section": f"groups.{group_name}",
                    "rule_name": rule.get("alert") or rule.get("record") or "unnamed-rule",
                    "expression": expression,
                }
            )

    for slo in payload.get("slos", []) or []:
        measurement = slo.get("measurement")
        if measurement:
            entries.append(
                {
                    "rule_file": str(path.resolve()),
                    "section": "slos",
                    "rule_name": slo.get("name", "unnamed-slo"),
                    "expression": measurement,
                }
            )

    for category, rules in (payload.get("alerting_rules", {}) or {}).items():
        for rule in rules or []:
            expression = rule.get("expr")
            if not expression:
                continue
            entries.append(
                {
                    "rule_file": str(path.resolve()),
                    "section": f"alerting_rules.{category}",
                    "rule_name": rule.get("alert", "unnamed-alert"),
                    "expression": expression,
                }
            )

    return entries


def _collect_dashboard_panels(panels: list[dict[str, Any]] | None, collected: list[dict[str, Any]]) -> None:
    for panel in panels or []:
        collected.append(panel)
        nested_panels = panel.get("panels")
        if isinstance(nested_panels, list):
            _collect_dashboard_panels(nested_panels, collected)


def _iter_dashboard_entries(path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    root = payload.get("dashboard", payload)
    panels: list[dict[str, Any]] = []
    _collect_dashboard_panels(root.get("panels"), panels)

    entries: list[dict[str, Any]] = []
    dashboard_title = root.get("title", path.stem)
    for panel in panels:
        panel_title = panel.get("title", f"panel-{panel.get('id', 'unknown')}")
        for index, target in enumerate(panel.get("targets", []) or [], start=1):
            expression = target.get("expr")
            if not expression:
                continue
            entries.append(
                {
                    "rule_file": str(path.resolve()),
                    "section": f"dashboard.{dashboard_title}",
                    "rule_name": f"{panel_title}#target-{index}",
                    "expression": expression,
                }
            )
    return entries


def build_reference_report(
    metrics_files: list[Path],
    rule_files: list[Path],
    dashboard_files: list[Path],
    declared_metric_python_files: list[Path],
) -> dict[str, Any]:
    observed_metrics = {name for path in metrics_files for name in _read_metrics_names(path)}
    declared_metrics = {name for path in declared_metric_python_files for name in _extract_declared_metrics_from_python(path)}
    available_metrics = sorted(observed_metrics | declared_metrics)
    available_metric_set = set(available_metrics)
    checks: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for rule_file in rule_files:
        payload = yaml.safe_load(rule_file.read_text(encoding="utf-8")) or {}
        for entry in _iter_rule_entries(rule_file, payload):
            references = extract_metric_references(entry["expression"])
            missing = sorted([metric for metric in references if metric not in available_metric_set])
            result = {
                **entry,
                "metric_references": references,
                "missing_metrics": missing,
                "status": "pass" if not missing else "missing_metrics",
            }
            checks.append(result)
            if missing:
                violations.append(result)

    for dashboard_file in dashboard_files:
        payload = json.loads(dashboard_file.read_text(encoding="utf-8"))
        for entry in _iter_dashboard_entries(dashboard_file, payload):
            references = extract_metric_references(entry["expression"])
            missing = sorted([metric for metric in references if metric not in available_metric_set])
            result = {
                **entry,
                "metric_references": references,
                "missing_metrics": missing,
                "status": "pass" if not missing else "missing_metrics",
            }
            checks.append(result)
            if missing:
                violations.append(result)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pass": not violations,
        "metrics_files": [str(path.resolve()) for path in metrics_files],
        "declared_metric_python_files": [str(path.resolve()) for path in declared_metric_python_files],
        "rule_files": [str(path.resolve()) for path in rule_files],
        "dashboard_files": [str(path.resolve()) for path in dashboard_files],
        "available_metrics": available_metrics,
        "violations": violations,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Prometheus rule metric references against runtime /metrics snapshots")
    parser.add_argument("--metrics-file", type=Path, action="append", required=True)
    parser.add_argument("--rule-file", type=Path, action="append", required=True)
    parser.add_argument("--dashboard-file", type=Path, action="append", default=[])
    parser.add_argument("--declared-metrics-python-file", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = build_reference_report(
        metrics_files=[path.resolve() for path in args.metrics_file],
        rule_files=[path.resolve() for path in args.rule_file],
        dashboard_files=[path.resolve() for path in args.dashboard_file],
        declared_metric_python_files=[path.resolve() for path in args.declared_metrics_python_file],
    )

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report["pass"]:
        print(f"[monitoring-rule-metrics] pass: {output_path}")
        return 0

    print(f"[monitoring-rule-metrics] failed: {output_path}")
    for item in report["violations"]:
        print(f"- {item['section']}::{item['rule_name']} missing metrics: {', '.join(item['missing_metrics'])}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
