from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "unified_response_contract_guard.py"


def run_guard(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_passes_when_route_declares_unified_response_model(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "health.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from app.core.responses import UnifiedResponse

router = APIRouter()

@router.get("/health", response_model=UnifiedResponse[dict[str, str]])
async def get_health() -> UnifiedResponse[dict[str, str]]:
    return UnifiedResponse(data={"status": "ok"})
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/health.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 1
    assert payload["checked_routes"] == 1


def test_passes_when_route_declares_unified_paginated_response_model(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "quotes.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from app.core.responses import UnifiedPaginatedResponse

router = APIRouter()

@router.get("/quotes", response_model=UnifiedPaginatedResponse[list[dict[str, str]]])
async def get_quotes():
    return {}
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/quotes.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0


def test_fails_when_route_missing_unified_response_model(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "quotes_bad.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

@router.get("/quotes")
async def get_quotes():
    return {"success": True, "data": []}
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/quotes_bad.py")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "web/backend/app/api/quotes_bad.py"
    assert payload["errors"][0]["endpoint"] == "get_quotes"
    assert payload["errors"][0]["rule_id"] == "unified-response-contract"


def test_fails_when_route_uses_non_unified_response_model(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "quotes_typed_bad.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QuoteResponse(BaseModel):
    symbol: str

@router.get("/quotes", response_model=QuoteResponse)
async def get_quotes():
    return {"symbol": "000001"}
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/quotes_typed_bad.py")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert "QuoteResponse" in payload["errors"][0]["message"]


def test_legacy_baseline_exempts_listed_endpoint(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "legacy_quotes.py"
    baseline = project_root / "governance" / "compliance" / "unified-response-contract-legacy-baseline.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    baseline.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QuoteResponse(BaseModel):
    symbol: str

@router.get("/quotes", response_model=QuoteResponse)
async def get_quotes():
    return {"symbol": "000001"}
""".strip(),
        encoding="utf-8",
    )
    baseline.write_text(
        json.dumps(
            {
                "version": "v0.1",
                "entries": [
                    {
                        "path": "web/backend/app/api/legacy_quotes.py",
                        "endpoints": ["get_quotes"],
                        "reason": "Legacy endpoint kept until a dedicated response-contract migration.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/legacy_quotes.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "legacy-baseline"
    assert "Legacy endpoint" in payload["results"][0]["message"]


def test_passes_for_raw_streaming_endpoint(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "streaming.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.get("/events")
async def stream_events():
    return EventSourceResponse(iter(()))
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/streaming.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "raw-exempt"


def test_passes_for_raw_response_endpoint(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "metrics.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/metrics")
async def metrics() -> Response:
    return Response(content="metric 1", media_type="text/plain")
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/metrics.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0


def test_passes_for_204_no_content_endpoint(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "delete_ok.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

@router.delete("/quotes/{symbol}", status_code=204)
async def delete_quote(symbol: str):
    return None
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/delete_ok.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0


def test_supports_positional_filenames_from_pre_commit(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "api" / "health.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from fastapi import APIRouter
from app.core.responses import UnifiedResponse

router = APIRouter()

@router.get("/health", response_model=UnifiedResponse[dict[str, str]])
async def get_health():
    return {"success": True, "data": {"status": "ok"}}
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "web/backend/app/api/health.py")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 1


def test_scope_paths_ignore_unrelated_existing_baseline_debt(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    bad = project_root / "web" / "backend" / "app" / "api" / "legacy_bad.py"
    ok = project_root / "web" / "backend" / "app" / "api" / "changed_ok.py"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(
        """
from fastapi import APIRouter

router = APIRouter()

@router.get("/legacy")
async def get_legacy():
    return {"success": True}
""".strip(),
        encoding="utf-8",
    )
    ok.write_text(
        """
from fastapi import APIRouter
from app.core.responses import UnifiedResponse

router = APIRouter()

@router.get("/changed", response_model=UnifiedResponse[dict[str, str]])
async def get_changed():
    return {"success": True, "data": {"status": "ok"}}
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/api/changed_ok.py")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 1


def test_incremental_mode_passes_when_no_paths_are_provided() -> None:
    completed = run_guard(PROJECT_ROOT)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 0
