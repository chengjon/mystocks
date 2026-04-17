from datetime import date

from app.core.database import DatabaseService


class _RedisRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str]] = []

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.calls.append((key, ttl, value))


def test_set_cache_data_serializes_date_values(monkeypatch):
    redis = _RedisRecorder()
    service = DatabaseService()

    monkeypatch.setattr(service, "_get_redis", lambda: redis)

    service.set_cache_data(
        "stocks_basic:1000:all",
        [{"symbol": "600519", "list_date": date(2001, 8, 27)}],
        ttl=1800,
    )

    assert redis.calls == [
        ("stocks_basic:1000:all", 1800, '[{"symbol": "600519", "list_date": "2001-08-27"}]'),
    ]
