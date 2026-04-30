from src.core.data_source.router import get_best_endpoint


class DummyManager:
    def __init__(self):
        self.registry = {
            "paid.endpoint": {
                "config": {
                    "data_category": "DAILY_KLINE",
                    "source_name": "paid-source",
                    "source_type": "tushare",
                    "cost": {"is_free": False},
                    "location": "shanghai",
                    "priority": 1,
                    "data_quality_score": 90,
                    "health_status": "healthy",
                }
            },
            "free.endpoint": {
                "config": {
                    "data_category": "DAILY_KLINE",
                    "source_name": "free-source",
                    "source_type": "akshare",
                    "cost": {"is_free": True},
                    "location": "beijing",
                    "priority": 2,
                    "data_quality_score": 80,
                    "health_status": "healthy",
                }
            },
        }

    def find_endpoints(self, **kwargs):
        from src.core.data_source.router import find_endpoints

        return find_endpoints(self, **kwargs)


def test_get_best_endpoint_uses_smart_router_selection():
    manager = DummyManager()

    best = get_best_endpoint(manager, "DAILY_KLINE")

    assert hasattr(manager, "smart_router")
    assert best is not None
    assert best["endpoint_name"] == "free.endpoint"
    assert best["config"]["source_type"] == "akshare"
    assert best["source_type"] == "akshare"
