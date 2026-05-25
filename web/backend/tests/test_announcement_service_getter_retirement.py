from __future__ import annotations

from app.services import announcement_service


def test_legacy_getter_and_module_singleton_are_retired():
    assert hasattr(announcement_service, "AnnouncementService")
    assert hasattr(announcement_service, "install_announcement_service")
    assert hasattr(announcement_service, "get_announcement_service_dependency")
    assert not hasattr(announcement_service, "get_announcement_service")
    assert not hasattr(announcement_service, "_announcement_service")
