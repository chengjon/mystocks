"""Regression tests for the DataService singleton provider seam."""

import pytest

from app.services import data_service as data_service_module
from app.services.data_service import (
    get_data_service,
    reset_data_service_provider,
    set_data_service_provider,
)


class FakeDataService:
    pass


@pytest.fixture(autouse=True)
def reset_provider_state():
    reset_data_service_provider()
    yield
    reset_data_service_provider()


def test_get_data_service_uses_registered_provider():
    service = FakeDataService()

    set_data_service_provider(lambda: service)

    assert get_data_service() is service


def test_reset_data_service_provider_restores_default_singleton(monkeypatch):
    service = FakeDataService()
    set_data_service_provider(lambda: service)
    assert get_data_service() is service

    monkeypatch.setattr(data_service_module, "DataService", FakeDataService)

    reset_data_service_provider()

    default_service = get_data_service()
    assert isinstance(default_service, FakeDataService)
    assert default_service is get_data_service()
    assert default_service is not service
