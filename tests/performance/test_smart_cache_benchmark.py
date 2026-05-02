import time

from src.core.data_source.cache import LRUCache
from src.core.data_source.smart_cache import SmartCache


class BlockingTtlBaselineCache:
    def __init__(self, ttl_seconds: float):
        self.cache = LRUCache(maxsize=16)
        self.ttl_seconds = ttl_seconds
        self.expires_at = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        expires_at = self.expires_at.get(key)
        now = time.perf_counter()
        if expires_at is None or now >= expires_at:
            self.misses += 1
            return None

        value = self.cache.get(key)
        if value is None:
            self.misses += 1
            return None

        self.hits += 1
        return value

    def set(self, key, value):
        self.cache[key] = value
        self.expires_at[key] = time.perf_counter() + self.ttl_seconds

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if not total:
            return 0.0
        return self.hits / total


def make_loader():
    state = {"version": 0}

    def load():
        time.sleep(0.015)
        state["version"] += 1
        return {"version": state["version"]}

    return load


def exercise_cache(get_or_load, access_count: int = 8, access_interval: float = 0.02) -> float:
    latencies = []
    for _ in range(access_count):
        time.sleep(access_interval)
        started = time.perf_counter()
        payload = get_or_load()
        latencies.append(time.perf_counter() - started)
        assert payload is not None
    return sum(latencies) / len(latencies)


def test_smart_cache_improves_hit_rate_and_mean_latency_over_blocking_ttl_baseline():
    ttl_seconds = 0.03

    smart_loader = make_loader()
    smart_cache = SmartCache(
        maxsize=16,
        default_ttl=ttl_seconds,
        refresh_threshold=0.5,
        soft_expiry=True,
        max_refresh_workers=1,
    )
    smart_cache.set("demo", smart_loader(), ttl=ttl_seconds, refresh_func=smart_loader)

    baseline_loader = make_loader()
    baseline_cache = BlockingTtlBaselineCache(ttl_seconds=ttl_seconds)
    baseline_cache.set("demo", baseline_loader())

    def smart_get_or_load():
        value = smart_cache.get("demo")
        if value is None:
            value = smart_loader()
            smart_cache.set("demo", value, ttl=ttl_seconds, refresh_func=smart_loader)
        return value

    def baseline_get_or_load():
        value = baseline_cache.get("demo")
        if value is None:
            value = baseline_loader()
            baseline_cache.set("demo", value)
        return value

    smart_avg_latency = exercise_cache(smart_get_or_load)
    baseline_avg_latency = exercise_cache(baseline_get_or_load)

    smart_cache.shutdown()
    smart_stats = smart_cache.get_stats()

    assert smart_stats["hit_rate"] > baseline_cache.hit_rate
    assert smart_avg_latency < baseline_avg_latency

