from app.services import wencai_service as wencai_service_module


def test_public_wencai_service_getter_is_retired():
    assert not hasattr(wencai_service_module, "get_wencai_service")


def test_wencai_service_class_remains_importable():
    assert hasattr(wencai_service_module, "WencaiService")
