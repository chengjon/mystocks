from __future__ import annotations

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_ROOT = PROJECT_ROOT / "web" / "frontend"
TYPE_INDEX = FRONTEND_ROOT / "src" / "api" / "types" / "index.ts"
TSCONFIG = FRONTEND_ROOT / "tsconfig.json"
EXTENSIONS_INDEX = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "index.ts"
UI_EXTENSION = FRONTEND_ROOT / "src" / "api" / "types" / "extensions" / "ui.ts"


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
    assert "market/index.ts exists" in completed.stdout
    assert "ui.ts exists" in completed.stdout


def test_ui_extension_defines_form_field_and_validation_exports() -> None:
    assert UI_EXTENSION.is_file()

    ui_content = UI_EXTENSION.read_text(encoding="utf-8")
    extensions_index_content = EXTENSIONS_INDEX.read_text(encoding="utf-8")

    assert "export interface FormField" in ui_content
    assert "export type FormValidationSchema" in ui_content
    assert "export * from './ui.ts'" in extensions_index_content


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
