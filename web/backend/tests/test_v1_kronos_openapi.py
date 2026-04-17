from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api.v1.analysis.kronos import router as kronos_router  # noqa: E402


def _build_openapi_schema() -> dict:
    app = FastAPI()
    app.include_router(kronos_router, prefix="/api/v1")
    return app.openapi()


def test_kronos_predict_openapi_includes_request_examples_and_error_examples():
    schema = _build_openapi_schema()

    predict_operation = schema["paths"]["/api/v1/kronos/predict"]["post"]
    request_examples = predict_operation["requestBody"]["content"]["application/json"]["examples"]

    assert "direct_candles" in request_examples
    assert "local_symbol_range" in request_examples
    assert "404" in predict_operation["responses"]
    assert "422" in predict_operation["responses"]
    assert "503" in predict_operation["responses"]
    assert (
        predict_operation["responses"]["503"]["content"]["application/json"]["example"]["errors"][0]["code"] == "TIMEOUT"
    )


def test_kronos_encode_openapi_includes_request_examples():
    schema = _build_openapi_schema()

    encode_operation = schema["paths"]["/api/v1/kronos/encode"]["post"]
    request_examples = encode_operation["requestBody"]["content"]["application/json"]["examples"]

    assert "encode_direct_candles" in request_examples
    assert "encode_local_symbol" in request_examples


def test_kronos_status_openapi_includes_success_example():
    schema = _build_openapi_schema()

    status_operation = schema["paths"]["/api/v1/kronos/status"]["get"]
    success_example = status_operation["responses"]["200"]["content"]["application/json"]["example"]

    assert success_example["message"] == "Kronos status retrieved"
    assert success_example["data"]["health"] == "healthy"
