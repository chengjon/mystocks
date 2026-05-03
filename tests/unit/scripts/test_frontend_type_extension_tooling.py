from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_ROOT = PROJECT_ROOT / "web" / "frontend"
TYPE_INDEX = FRONTEND_ROOT / "src" / "api" / "types" / "index.ts"
TSCONFIG = FRONTEND_ROOT / "tsconfig.json"
EXTENSIONS_INDEX = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "index.ts"
STRATEGY_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "strategy" / "index.ts"
COMMON_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "common" / "index.ts"
UI_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "ui" / "index.ts"
API_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "api" / "index.ts"
UTILS_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "utils" / "index.ts"


def _run_node_script(relative_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", relative_path],
        cwd=FRONTEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_main_type_index_exports_extensions_namespace() -> None:
    content = TYPE_INDEX.read_text(encoding="utf-8")

    assert "from './extensions'" in content


def test_frontend_tsconfig_includes_extension_types_in_typecheck_scope() -> None:
    content = TSCONFIG.read_text(encoding="utf-8")

    assert '"src/api/types/extensions/**/*"' not in content


def test_validate_types_script_succeeds_against_repo_truth_layout() -> None:
    completed = _run_node_script("scripts/validate-types.js")

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "Main index.ts exports extensions" in completed.stdout
    assert "strategy/index.ts exists" in completed.stdout
    assert "market/index.ts exists" in completed.stdout
    assert "common/index.ts exists" in completed.stdout
    assert "ui/index.ts exists" in completed.stdout
    assert "api/index.ts exists" in completed.stdout
    assert "utils/index.ts exists" in completed.stdout


def test_extension_subdirectories_define_canonical_repo_truth_layout() -> None:
    assert STRATEGY_EXTENSION.is_file()
    assert COMMON_EXTENSION.is_file()
    assert UI_EXTENSION.is_file()
    assert API_EXTENSION.is_file()
    assert UTILS_EXTENSION.is_file()

    ui_content = UI_EXTENSION.read_text(encoding="utf-8")
    extensions_index_content = EXTENSIONS_INDEX.read_text(encoding="utf-8")

    assert "export interface FormField" in ui_content
    assert "export type FormValidationSchema" in ui_content
    assert "export * from './strategy/index.ts';" in extensions_index_content
    assert "export * from './common/index.ts';" in extensions_index_content
    assert "export * from './ui/index.ts';" in extensions_index_content
    assert "export * from './api/index.ts';" in extensions_index_content
    assert "export * from './utils/index.ts';" in extensions_index_content


def test_check_type_conflicts_script_reports_clean_repo_truth_surface() -> None:
    completed = _run_node_script("scripts/check-type-conflicts.js")

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "No type conflicts detected" in completed.stdout


def test_generate_type_usage_script_emits_usage_summary_json() -> None:
    completed = _run_node_script("scripts/generate-type-usage.js")

    assert completed.returncode == 0, completed.stderr or completed.stdout

    payload = json.loads(completed.stdout)

    assert payload["extensions"]["files"] >= 1
    assert payload["extensions"]["exported_types"] >= 1
    assert payload["main_index"]["exports_extensions"] is True


def test_generate_frontend_types_preserves_extensions_namespace_in_main_index() -> None:
    completed = subprocess.run(
        ["python", "scripts/generate_frontend_types.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout

    content = TYPE_INDEX.read_text(encoding="utf-8")
    assert "export * as extensions from './extensions';" in content


def test_audit_type_extension_quality_reports_clean_naming_and_jsdoc() -> None:
    completed = _run_node_script("scripts/audit-type-extension-quality.js")

    assert completed.returncode == 0, completed.stderr or completed.stdout

    payload = json.loads(completed.stdout)

    assert payload["naming"]["ok"] is True
    assert payload["naming"]["violations"] == []
    assert payload["jsdoc"]["ok"] is True
    assert payload["jsdoc"]["missing"] == []
    assert payload["unused"]["count"] == 0
    assert "StrategyParametersVM" not in payload["unused"]["names"]
    assert "FormValidationRule" not in payload["unused"]["names"]
    assert "date_type" not in payload["unused"]["names"]
    assert "FormValidationSchema" not in payload["unused"]["names"]
    assert "FormValidationState" not in payload["unused"]["names"]
    assert "StrategyComparisonDataVM" not in payload["unused"]["names"]
    assert "StrategyOptimizationRequestVM" not in payload["unused"]["names"]
    assert "StrategyOptimizationResultVM" not in payload["unused"]["names"]
    assert "PaginatedResponseVM" not in payload["unused"]["names"]
    assert "APIErrorVM" not in payload["unused"]["names"]
    assert "PaginationParamsVM" not in payload["unused"]["names"]
    assert "SearchParamsVM" not in payload["unused"]["names"]
    assert "FilterParamsVM" not in payload["unused"]["names"]
    assert "SortParamsVM" not in payload["unused"]["names"]
    assert "ValidationResultVM" not in payload["unused"]["names"]
    assert "UploadResultVM" not in payload["unused"]["names"]
    assert "UploadProgressVM" not in payload["unused"]["names"]
    assert "WSSubscriptionVM" not in payload["unused"]["names"]
    assert "WSDataMessageVM" not in payload["unused"]["names"]
    assert "WSErrorMessageVM" not in payload["unused"]["names"]
    assert "WSSubscription" not in payload["unused"]["names"]
    assert "WSDataMessage" not in payload["unused"]["names"]
    assert "SearchParams" not in payload["unused"]["names"]
    assert "UploadResult" not in payload["unused"]["names"]
    assert "KeysOfType" not in payload["unused"]["names"]
    assert "AsyncFunction" not in payload["unused"]["names"]
    assert "TimeoutOptions" not in payload["unused"]["names"]
    assert "HttpMethod" not in payload["unused"]["names"]
    assert "LoadingState" not in payload["unused"]["names"]
    assert "LanguageCode" not in payload["unused"]["names"]
    assert "CurrencyCode" not in payload["unused"]["names"]
