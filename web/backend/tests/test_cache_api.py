"""
缓存 API 端点测试

测试缓存管理的HTTP API端点。

Test Coverage:
- GET /cache/status - 缓存统计
- GET /cache/{symbol}/{type} - 读取缓存
- POST /cache/{symbol}/{type} - 写入缓存
- DELETE /cache/{symbol} - 清除符号缓存
- DELETE /cache - 清除所有缓存
- GET /cache/{symbol}/{type}/fresh - 检查新鲜度
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.api.cache import router
from app.core.cache_manager import reset_cache_manager, get_cache_manager
from app.core.cache_integration import reset_cache_integration


@pytest.fixture
def client():
    """创建测试客户端"""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


@pytest.fixture
def setup_teardown():
    """设置和清理"""
    reset_cache_manager()
    reset_cache_integration()
    yield
    reset_cache_manager()
    reset_cache_integration()


class TestCacheStatusAPI:
    """测试缓存统计API"""

    def test_get_cache_status_success(self, client, setup_teardown):
        """测试成功获取缓存统计"""
        response = client.get("/api/cache/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "hit_rate" in data["data"]
        assert "total_reads" in data["data"]
        assert "total_writes" in data["data"]

    def test_get_cache_status_structure(self, client, setup_teardown):
        """测试缓存统计的数据结构"""
        response = client.get("/api/cache/status")
        data = response.json()

        stats = data["data"]
        assert isinstance(stats, dict)
        assert isinstance(stats.get("hit_rate"), (int, float))
        assert isinstance(stats.get("cache_hits"), int)
        assert isinstance(stats.get("cache_misses"), int)
        assert isinstance(stats.get("total_reads"), int)
        assert isinstance(stats.get("total_writes"), int)


class TestCacheReadAPI:
    """测试缓存读取API"""

    def test_read_cache_hit(self, client, setup_teardown):
        """测试缓存命中的读取"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 读取缓存
        response = client.get("/api/cache/000001/fund_flow")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["source"] == "cache"
        assert data["data"] is not None

    def test_read_cache_miss(self, client, setup_teardown):
        """测试缓存未命中的读取"""
        response = client.get("/api/cache/999999/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"] is None

    def test_read_cache_with_timeframe(self, client, setup_teardown):
        """测试带timeframe的缓存读取"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="3d",
            data={"value": 200},
        )

        # 读取缓存
        response = client.get("/api/cache/000001/fund_flow?timeframe=3d")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_read_cache_empty_symbol(self, client, setup_teardown):
        """测试空符号的读取"""
        response = client.get("/api/cache//fund_flow")

        # 应该返回400或404
        assert response.status_code in [400, 404, 405]

    def test_read_cache_empty_type(self, client, setup_teardown):
        """测试空类型的读取"""
        response = client.get("/api/cache/000001/")

        # 应该返回400或404
        assert response.status_code in [400, 404, 405]


class TestCacheWriteAPI:
    """测试缓存写入API"""

    def test_write_cache_success(self, client, setup_teardown):
        """测试成功写入缓存"""
        response = client.post(
            "/api/cache/000001/fund_flow",
            json={"value": 100, "rate": 0.5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["symbol"] == "000001"
        assert data["data_type"] == "fund_flow"

    def test_write_cache_with_ttl(self, client, setup_teardown):
        """测试带TTL的缓存写入"""
        response = client.post(
            "/api/cache/000001/fund_flow?ttl_days=1",
            json={"value": 100},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["ttl_days"] == 1

    def test_write_cache_invalid_data(self, client, setup_teardown):
        """测试无效数据的写入"""
        response = client.post(
            "/api/cache/000001/fund_flow",
            json=None,
        )

        assert response.status_code in [400, 422]

    def test_write_cache_invalid_symbol(self, client, setup_teardown):
        """测试无效符号的写入"""
        response = client.post(
            "/api/cache//fund_flow",
            json={"value": 100},
        )

        assert response.status_code in [400, 404, 405]

    def test_write_cache_invalid_ttl(self, client, setup_teardown):
        """测试无效TTL的写入"""
        response = client.post(
            "/api/cache/000001/fund_flow?ttl_days=0",
            json={"value": 100},
        )

        assert response.status_code == 400

    def test_write_and_read_consistency(self, client, setup_teardown):
        """测试写入和读取的一致性"""
        test_data = {"value": 100, "rate": 0.5}

        # 写入
        write_response = client.post(
            "/api/cache/000001/fund_flow",
            json=test_data,
        )
        assert write_response.status_code == 200

        # 读取
        read_response = client.get("/api/cache/000001/fund_flow")
        assert read_response.status_code == 200
        read_data = read_response.json()
        assert read_data["data"] == test_data


class TestCacheDeleteAPI:
    """测试缓存删除API"""

    def test_delete_symbol_cache_success(self, client, setup_teardown):
        """测试成功删除符号缓存"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 删除
        response = client.delete("/api/cache/000001")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_symbol_cache_empty(self, client, setup_teardown):
        """测试删除不存在的符号缓存"""
        response = client.delete("/api/cache/999999")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_all_cache_without_confirm(self, client, setup_teardown):
        """测试不确认时删除所有缓存"""
        response = client.delete("/api/cache")

        # 应该失败
        assert response.status_code == 400

    def test_delete_all_cache_with_confirm(self, client, setup_teardown):
        """测试确认后删除所有缓存"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        for i in range(5):
            cache_mgr.write_to_cache(
                symbol=f"00000{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        # 删除所有缓存
        response = client.delete("/api/cache?confirm=true")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestCacheFreshnessAPI:
    """测试缓存新鲜度检查API"""

    def test_check_freshness_fresh(self, client, setup_teardown):
        """测试新鲜缓存的检查"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 检查新鲜度
        response = client.get("/api/cache/000001/fund_flow/fresh")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_fresh"] is True

    def test_check_freshness_not_exists(self, client, setup_teardown):
        """测试不存在缓存的新鲜度检查"""
        response = client.get("/api/cache/999999/nonexistent/fresh")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 不存在的缓存不是新鲜的
        assert data["is_fresh"] is False

    def test_check_freshness_custom_age(self, client, setup_teardown):
        """测试自定义缓存年龄的新鲜度检查"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 检查新鲜度（1天）
        response = client.get("/api/cache/000001/fund_flow/fresh?max_age_days=1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["max_age_days"] == 1


class TestCacheAPIEdgeCases:
    """测试缓存API的边界情况"""

    def test_special_characters_in_symbol(self, client, setup_teardown):
        """测试特殊字符的符号"""
        response = client.post(
            "/api/cache/000001@/fund_flow",
            json={"value": 100},
        )

        # 应该能够处理
        assert response.status_code in [200, 400]

    def test_very_large_data(self, client, setup_teardown):
        """测试非常大的数据"""
        large_data = {"values": list(range(10000))}

        response = client.post(
            "/api/cache/000001/fund_flow",
            json=large_data,
        )

        # 应该能够处理
        assert response.status_code in [200, 400, 413]

    def test_concurrent_reads(self, client, setup_teardown):
        """测试并发读取"""
        # 预先写入缓存
        cache_mgr = get_cache_manager()
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 多次读取
        for _ in range(10):
            response = client.get("/api/cache/000001/fund_flow")
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_write_read_delete_cycle(self, client, setup_teardown):
        """测试完整的写-读-删周期"""
        symbol = "000001"
        data_type = "fund_flow"
        test_data = {"value": 100}

        # 1. 写入
        write_response = client.post(
            f"/api/cache/{symbol}/{data_type}",
            json=test_data,
        )
        assert write_response.status_code == 200
        assert write_response.json()["success"] is True

        # 2. 读取
        read_response = client.get(f"/api/cache/{symbol}/{data_type}")
        assert read_response.status_code == 200
        assert read_response.json()["success"] is True

        # 3. 删除
        delete_response = client.delete(f"/api/cache/{symbol}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True


class TestCacheAPIResponseFormat:
    """测试缓存API的响应格式"""

    def test_response_includes_timestamp(self, client, setup_teardown):
        """测试响应包含时间戳"""
        response = client.get("/api/cache/status")
        data = response.json()

        assert "timestamp" in data
        # 验证时间戳格式
        try:
            datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail("时间戳格式不正确")

    def test_response_includes_success_flag(self, client, setup_teardown):
        """测试响应包含成功标志"""
        response = client.get("/api/cache/status")
        data = response.json()

        assert "success" in data
        assert isinstance(data["success"], bool)

    def test_error_response_structure(self, client, setup_teardown):
        """测试错误响应结构"""
        response = client.get("/api/cache/000001/fund_flow/fresh?max_age_days=0")

        assert response.status_code == 400
        # 检查错误响应有detail
        assert "detail" in response.json() or "detail" in str(response.content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
