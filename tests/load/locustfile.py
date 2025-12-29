"""
MyStocks API压力测试脚本 - Locust
测试目标：验证API在高并发情况下的性能表现
"""

from locust import HttpUser, task, between, events
import random


class StockAPIUser(HttpUser):
    """MyStocks API用户模拟"""

    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时执行"""
        # 获取健康检查
        self.client.get("/health")

    @task(3)
    def health_check(self):
        """健康检查（高频）"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check status not healthy")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def csrf_token(self):
        """获取CSRF Token（中频）"""
        self.client.get("/api/csrf-token")

    @task(2)
    def root_endpoint(self):
        """根路径（中频）"""
        self.client.get("/")

    @task(1)
    def docs_endpoint(self):
        """API文档（低频）"""
        self.client.get("/api/docs")

    @task(1)
    def redoc_endpoint(self):
        """ReDoc文档（低频）"""
        self.client.get("/api/redoc")

    @task(1)
    def socketio_status(self):
        """Socket.IO状态（低频）"""
        self.client.get("/api/socketio-status")

    @task(1)
    def metrics_endpoint(self):
        """Prometheus指标（低频）"""
        self.client.get("/metrics", name="/metrics (Prometheus)")

    @task(1)
    def openapi_spec(self):
        """OpenAPI规范（低频）"""
        self.client.get("/openapi.json", name="/openapi.json")


class MarketDataUser(HttpUser):
    """市场数据用户模拟"""

    wait_time = between(2, 5)

    @task(5)
    def get_stock_list(self):
        """获取股票列表（高频）"""
        symbols = ["000001", "000002", "600000", "600519", "000725"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/data/stock/{symbol}", name="/api/data/stock/{symbol}")

    @task(3)
    def get_kline_data(self):
        """获取K线数据（中频）"""
        symbols = ["000001", "600000", "600519"]
        symbol = random.choice(symbols)
        intervals = ["1d", "1w", "1m"]
        interval = random.choice(intervals)

        self.client.get(
            f"/api/data/kline/{symbol}", params={"interval": interval, "limit": 100}, name="/api/data/kline/{symbol}"
        )

    @task(2)
    def get_realtime_data(self):
        """获取实时数据（中频）"""
        symbols = ["000001", "000002", "600000", "600519"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/data/realtime/{symbol}", name="/api/data/realtime/{symbol}")

    @task(1)
    def get_batch_realtime(self):
        """批量获取实时数据（低频）"""
        symbols = ["000001", "000002", "600000", "600519", "000725"]
        self.client.get(
            "/api/data/batch-realtime", params={"symbols": ",".join(symbols)}, name="/api/data/batch-realtime"
        )


class TechnicalAnalysisUser(HttpUser):
    """技术分析用户模拟"""

    wait_time = between(3, 6)

    @task(3)
    def calculate_indicator(self):
        """计算技术指标（高频）"""
        symbols = ["000001", "600000"]
        symbol = random.choice(symbols)
        indicators = ["MACD", "RSI", "KDJ", "BOLL"]
        indicator = random.choice(indicators)

        self.client.get(f"/api/indicators/{symbol}/{indicator}", name="/api/indicators/{symbol}/{indicator}")

    @task(2)
    def get_multiple_indicators(self):
        """获取多个指标（中频）"""
        symbols = ["000001", "600519"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/indicators/{symbol}/all", name="/api/indicators/{symbol}/all")

    @task(1)
    def technical_analysis(self):
        """技术分析（低频）"""
        symbols = ["000001", "600000"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/technical-analysis/{symbol}", name="/api/technical-analysis/{symbol}")


class CacheUser(HttpUser):
    """缓存用户模拟"""

    wait_time = between(2, 4)

    @task(3)
    def get_cache_stats(self):
        """获取缓存统计（高频）"""
        self.client.get("/api/cache/stats", name="/api/cache/stats")

    @task(2)
    def get_cache_info(self):
        """获取缓存信息（中频）"""
        self.client.get("/api/cache/info", name="/api/cache/info")

    @task(1)
    def clear_cache(self):
        """清除缓存（低频）"""
        with self.client.delete("/api/cache", catch_response=True) as response:
            if response.status_code in [200, 204]:
                response.success()
            else:
                response.failure(f"Failed to clear cache: {response.status_code}")


class StrategyUser(HttpUser):
    """策略用户模拟"""

    wait_time = between(3, 7)

    @task(3)
    def get_strategies(self):
        """获取策略列表（高频）"""
        self.client.get("/api/strategies", name="/api/strategies")

    @task(2)
    def execute_strategy(self):
        """执行策略（中频）"""
        strategy_id = random.choice(["value", "growth", "balanced"])
        self.client.post(
            "/api/strategy/execute",
            json={"strategy_id": strategy_id, "params": {"top_n": 20, "min_score": 60}},
            name="/api/strategy/execute",
        )

    @task(1)
    def get_strategy_result(self):
        """获取策略结果（低频）"""
        strategy_id = random.choice(["value", "growth"])
        self.client.get(f"/api/strategy/{strategy_id}/result", name="/api/strategy/{strategy_id}/result")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的回调"""
    print("\n" + "=" * 50)
    print("MyStocks API压力测试开始")
    print("=" * 50 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试停止时的回调"""
    print("\n" + "=" * 50)
    print("MyStocks API压力测试结束")
    print("=" * 50 + "\n")

    if environment.stats.total.fail_ratio > 0.01:  # 失败率 > 1%
        print(f"⚠️ 警告：失败率过高 ({environment.stats.total.fail_ratio:.2%})")
    else:
        print(f"✅ 失败率正常 ({environment.stats.total.fail_ratio:.2%})")

    print(f"总请求数: {environment.stats.total.num_requests}")
    print(f"RPS: {environment.stats.total.total_rps:.2f}")
    print(f"平均响应时间: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"P95响应时间: {environment.stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99响应时间: {environment.stats.total.get_response_time_percentile(0.99):.2f}ms")
