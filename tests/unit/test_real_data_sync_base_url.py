from __future__ import annotations

from tests.real_data_synchronization_test import RealDataSynchronizationTester


def test_real_data_tester_uses_base_url_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")

    tester = RealDataSynchronizationTester()

    assert tester.base_url == "http://localhost:8000"


def test_real_data_tester_explicit_base_url_overrides_environment(monkeypatch) -> None:
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")

    tester = RealDataSynchronizationTester("http://localhost:9000")

    assert tester.base_url == "http://localhost:9000"
