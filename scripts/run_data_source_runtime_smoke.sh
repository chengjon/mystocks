#!/usr/bin/env bash
set -euo pipefail

OPENSTOCK_DIR="${OPENSTOCK_DIR:-/opt/claude/openstock}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/matplotlib-openstock-smoke}"

if [[ ! -d "${OPENSTOCK_DIR}" ]]; then
  echo "openstock directory not found: ${OPENSTOCK_DIR}" >&2
  exit 1
fi

(
  cd "${OPENSTOCK_DIR}"
  pytest tests/test_runtime_contract.py tests/test_akshare_runtime_pilot.py tests/test_market_stream_contract.py -q -p no:timing -p no:tdd-guard -p no:cacheprovider

  if [[ "${OPENSTOCK_SKIP_AKSHARE_REAL_SMOKE:-0}" != "1" ]]; then
    python - <<'PY'
import contextlib
import io

from fastapi.testclient import TestClient

from openstock.app import create_app

buffer = io.StringIO()
with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
    response = TestClient(create_app()).post(
        "/data/fetch",
        json={
            "data_category": "REALTIME_QUOTES",
            "params": {"limit": 1},
            "request_id": "smoke-akshare-real",
            "timeout_ms": 15000,
        },
    )

response.raise_for_status()
payload = response.json()
assert payload["source"] == "akshare", payload
assert payload["endpoint_name"] in {"akshare.stock_zh_a_spot", "akshare.stock_info_a_code_name"}, payload
assert payload["data"], payload
assert payload["data"][0].get("symbol"), payload["data"][0]
print(
    "openstock akshare real smoke passed:",
    payload["endpoint_name"],
    payload["data"][0].get("symbol"),
    payload["data"][0].get("name"),
    payload["quality_flags"],
)
PY
  fi
)

pytest tests/integration/data_source/test_remote_data_source_client_contract.py -q --no-cov -p no:cacheprovider
pytest tests/integration/data_source/test_akshare_runtime_pilot.py -q --no-cov -p no:cacheprovider
pytest tests/integration/data_source/test_market_stream_contract.py -q --no-cov -p no:cacheprovider
pytest tests/integration/data_source/test_mcp_access_modes.py -q --no-cov -p no:cacheprovider
pytest tests/integration/data_source/test_data_source_public_api_parity.py -q --no-cov -p no:cacheprovider
