import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from src.adapters.byapi_adapter import ByapiAdapter


def test_byapi_adapter_defaults_to_https_when_env_missing(monkeypatch):
    for key in ("BYAPI_KEY", "BYAPI_LICENCE", "BYAPI_LICENSE", "BYAPI_TOKEN", "BYAPI_BASE_URL"):
        monkeypatch.delenv(key, raising=False)

    adapter = ByapiAdapter()

    assert adapter.licence == "04C01BF1-7F2F-41A3-B470-1F81F14B1FC8"
    assert adapter.base_url == "https://api.biyingapi.com"


def test_byapi_adapter_prefers_runtime_env_defaults(monkeypatch):
    monkeypatch.setenv("BYAPI_KEY", "ENV-LICENCE")
    monkeypatch.setenv("BYAPI_BASE_URL", "https://env.api.com")

    adapter = ByapiAdapter()

    assert adapter.licence == "ENV-LICENCE"
    assert adapter.base_url == "https://env.api.com"


def test_byapi_adapter_explicit_args_override_runtime_env(monkeypatch):
    monkeypatch.setenv("BYAPI_KEY", "ENV-LICENCE")
    monkeypatch.setenv("BYAPI_BASE_URL", "https://env.api.com")

    adapter = ByapiAdapter(licence="EXPLICIT-LICENCE", base_url="https://explicit.api.com")

    assert adapter.licence == "EXPLICIT-LICENCE"
    assert adapter.base_url == "https://explicit.api.com"
