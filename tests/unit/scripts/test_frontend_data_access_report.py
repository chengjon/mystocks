from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "frontend_data_access_report.py"


def load_module():
    spec = importlib.util.spec_from_file_location("frontend_data_access_report", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_report_tracks_direct_view_imports_and_empty_catches(tmp_path: Path) -> None:
    module = load_module()

    repo_root = tmp_path
    frontend_root = repo_root / "web" / "frontend" / "src"
    view_root = frontend_root / "views"
    view_root.mkdir(parents=True)
    (frontend_root / "services").mkdir(parents=True)
    (frontend_root / "stores").mkdir(parents=True)

    (view_root / "TradeView.vue").write_text(
        "<script setup lang=\"ts\">\nimport { apiClient } from '@/api/apiClient'\n</script>\n",
        encoding="utf-8",
    )
    (frontend_root / "services" / "dashboard.ts").write_text(
        "import { apiClient } from '@/api/apiClient'\nexport async function load() { return apiClient.get('/x') }\n",
        encoding="utf-8",
    )
    (frontend_root / "stores" / "signals.ts").write_text(
        "export async function loadSignals() { return Promise.resolve().catch(() => {}) }\n",
        encoding="utf-8",
    )

    module.REPO_ROOT = repo_root
    module.FRONTEND_ROOT = frontend_root
    module.VIEW_ROOT = view_root

    report = module.build_report()

    assert report["summary"] == {
        "direct_api_client_imports_in_views": 1,
        "empty_catch_handlers": 1,
    }
    assert report["findings"] == {
        "direct_api_client_imports_in_views": ["web/frontend/src/views/TradeView.vue"],
        "empty_catch_handlers": ["web/frontend/src/stores/signals.ts"],
    }


def test_main_returns_non_zero_in_strict_mode_when_findings_exist(monkeypatch) -> None:
    module = load_module()

    monkeypatch.setattr(
        module,
        "build_report",
        lambda: {
            "summary": {
                "direct_api_client_imports_in_views": 1,
                "empty_catch_handlers": 0,
            },
            "findings": {
                "direct_api_client_imports_in_views": ["web/frontend/src/views/TradeView.vue"],
                "empty_catch_handlers": [],
            },
        },
    )
    monkeypatch.setattr(module.argparse.ArgumentParser, "parse_args", lambda _self: module.argparse.Namespace(strict=True))

    assert module.main() == 1
