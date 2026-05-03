#!/usr/bin/env python3
"""Collect local AkShare market-function availability for the tracked expansion scope."""

from __future__ import annotations

import argparse
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports/analysis/akshare-market-function-availability.json"
CANONICAL_FUNCTIONS = [
    "stock_hot_follow_xq",
    "stock_board_change_em",
    "stock_news_main_em",
    "stock_zt_pool_em",
    "stock_dt_pool_em",
    "stock_strong_pool_em",
    "stock_weak_pool_em",
    "stock_changes_em",
    "stock_new_em",
]
GENERIC_TOKENS = {"stock", "em", "zh", "a"}
PREFERRED_HELP_CANDIDATES = {
    "stock_dt_pool_em": ("stock_zt_pool_dtgc_em",),
    "stock_strong_pool_em": ("stock_zt_pool_strong_em",),
    "stock_new_em": ("stock_zt_pool_sub_new_em",),
}


def _normalize_tokens(name: str) -> list[str]:
    tokens = [token for token in name.split("_") if token and token not in GENERIC_TOKENS]
    return tokens or [token for token in name.split("_") if token]


def _token_similarity(target_token: str, candidate_token: str) -> int:
    if target_token == candidate_token:
        return 3
    if min(len(target_token), len(candidate_token)) <= 2 and candidate_token.startswith(target_token):
        return 2
    if min(len(target_token), len(candidate_token)) <= 2 and target_token.startswith(candidate_token):
        return 2
    return 0


def _find_help_candidates(module: Any, target_name: str, limit: int = 3) -> list[str]:
    target_tokens = _normalize_tokens(target_name)
    preferred_candidates: list[str] = []
    for candidate_name in PREFERRED_HELP_CANDIDATES.get(target_name, ()):
        candidate_obj = getattr(module, candidate_name, None)
        if callable(candidate_obj):
            preferred_candidates.append(candidate_name)

    ranked_candidates: list[tuple[int, int, str]] = []
    for candidate_name in dir(module):
        if candidate_name == target_name or candidate_name in preferred_candidates or not candidate_name.startswith("stock_"):
            continue
        candidate_obj = getattr(module, candidate_name, None)
        if not callable(candidate_obj):
            continue
        candidate_tokens = _normalize_tokens(candidate_name)
        matched_count = 0
        score = 0
        for target_token in target_tokens:
            token_score = max((_token_similarity(target_token, candidate) for candidate in candidate_tokens), default=0)
            if token_score > 0:
                matched_count += 1
                score += token_score
        if matched_count != len(target_tokens):
            continue
        extra_tokens = max(len(candidate_tokens) - len(target_tokens), 0)
        ranked_candidates.append((score, -extra_tokens, candidate_name))

    ranked_candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    ranked_names = [candidate_name for _, _, candidate_name in ranked_candidates]
    return (preferred_candidates + ranked_names)[:limit]


def collect_availability(module_name: str, function_names: list[str]) -> tuple[dict[str, Any], int]:
    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "report_type": "akshare_market_function_availability",
        "project_root": str(PROJECT_ROOT),
        "module": module_name,
        "functions": [],
    }
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        payload["import_ok"] = False
        payload["import_error"] = str(exc)
        payload["summary"] = {
            "tracked_count": len(function_names),
            "available_count": 0,
            "missing_count": len(function_names),
            "available_functions": [],
            "missing_functions": function_names,
        }
        return payload, 1

    payload["import_ok"] = True
    payload["module_version"] = getattr(module, "__version__", None)

    function_rows: list[dict[str, Any]] = []
    available_functions: list[str] = []
    missing_functions: list[str] = []
    help_candidate_functions: dict[str, list[str]] = {}
    for name in function_names:
        available = hasattr(module, name)
        row = {"name": name, "available": available}
        if available:
            available_functions.append(name)
        else:
            missing_functions.append(name)
            help_candidates = _find_help_candidates(module, name)
            row["help_candidates"] = help_candidates
            if help_candidates:
                help_candidate_functions[name] = help_candidates
        function_rows.append(row)

    payload["functions"] = function_rows
    payload["summary"] = {
        "tracked_count": len(function_names),
        "available_count": len(available_functions),
        "missing_count": len(missing_functions),
        "available_functions": available_functions,
        "missing_functions": missing_functions,
        "help_candidate_functions": help_candidate_functions,
    }
    return payload, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect local AkShare market function availability")
    parser.add_argument("--module", default="akshare", help="Python module to inspect; defaults to akshare")
    parser.add_argument(
        "--function",
        action="append",
        dest="functions",
        help="Function/attribute to probe; repeatable. Defaults to the tracked expand-akshare-data-sources section 6 set.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    function_names = args.functions or CANONICAL_FUNCTIONS
    payload, exit_code = collect_availability(module_name=args.module, function_names=function_names)

    output_path = args.output if args.output.is_absolute() else (PROJECT_ROOT / args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
