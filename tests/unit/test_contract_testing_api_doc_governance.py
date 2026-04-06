from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = PROJECT_ROOT / "docs" / "api" / "CONTRACT_TESTING_API.md"


def test_contract_testing_api_doc_marks_legacy_snapshot_and_current_runtime_entries() -> None:
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "历史快照" in content
    assert "当前实现入口" in content
    assert "web/backend/app/api/contract/services/contract_testing.py" in content
    assert "tests/contract/contract_engine.py" in content
    assert "运行时生成的 OpenAPI" in content
    assert "显式 spec_path / openapi_spec_path 只作为兼容覆盖" in content
