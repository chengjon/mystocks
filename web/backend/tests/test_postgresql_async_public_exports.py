import importlib


def test_postgresql_async_v3_re_exports_singleton_helpers():
    public_module = importlib.import_module("src.monitoring.infrastructure.postgresql_async_v3")
    singleton_module = importlib.import_module("src.monitoring.infrastructure._postgresql_async_v3_singleton")

    assert public_module.get_postgres_async is singleton_module.get_postgres_async
    assert public_module.initialize_postgres_async is singleton_module.initialize_postgres_async
    assert public_module.close_postgres_async is singleton_module.close_postgres_async
