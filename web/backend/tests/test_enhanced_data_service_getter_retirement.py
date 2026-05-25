from pathlib import Path

from app.services import data_service_enhanced as enhanced_data_service_module


def test_public_enhanced_data_service_getter_is_retired():
    assert not hasattr(enhanced_data_service_module, "get_enhanced_data_service")


def test_enhanced_data_service_class_remains_importable():
    assert hasattr(enhanced_data_service_module, "EnhancedDataService")


def test_enhanced_data_service_singleton_state_is_retired():
    source = Path(enhanced_data_service_module.__file__).read_text()

    assert "_enhanced_data_service" not in source
    assert "get_enhanced_data_service()" not in source
