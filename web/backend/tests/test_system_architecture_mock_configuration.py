from __future__ import annotations

import importlib
from pathlib import Path

import pytest

module = importlib.import_module("app.api.system.get_system_architecture")


def test_system_architecture_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_system_architecture_endpoint_returns_runtime_payload():
    result = await module.get_system_architecture()

    assert result["success"] is True
    assert result["data"]["simplification"]["after"]["databases"] == 2
