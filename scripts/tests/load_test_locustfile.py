"""
Locust Load Testing Suite for MyStocks API
用于模拟1000并发用户的压测脚本，测试API、WebSocket和数据库性能

任务14.1: Locust压测脚本和用户行为建模
"""

import os
import sys
import random
from pathlib import Path

# 计算项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from locust import HttpUser, TaskSet, task, between, events, constant_pacing
import structlog

logger = structlog.get_logger()


class LoadTestConfig:
    """压测配置"""

    # API服务地址
    API_HOST = os.getenv("API_HOST", "http://localhost:8000")

    # 测试参数
    TARGET_USERS = 1000  # 目标并发用户数
    RAMP_UP_TIME = 300  # 加载时间(秒)
    TEST_DURATION = 600  # 测试持续时间(秒)

    # 用户数据
    STOCKS = [
        "000001",
        "000002",
        "600000",
        "600001",
        "000858",
        "601398",
        "601939",
        "600519",
        "000333",
        "000651",
        "002475",
        "601988",
    ]

    INDUSTRIES_CSRC = ["A01", "A02", "A03", "B01", "B02", "C01", "C02", "C03"]

    INDUSTRIES_SW_L1 = [
        "801010",
        "801020",
        "801030",
        "801040",
        "801050",
        "801080",
        "801110",
        "801120",
        "801130",
        "801140",
        "801150",
        "801160",
    ]


class StockBehaviors(TaskSet):
    """股票查询行为集 - 高频操作"""

    def on_start(self):
        """用户启动时初始化"""
        self.auth_token = None
        self.csrf_token = None
        self.watchlist = []
        self.login()

    def on_stop(self):
        """用户结束时清理"""
        if self.auth_token:
            self.logout()

    def login(self):
        """登录获取Token"""
        try:
            # 获取CSRF Token
            response = self.client.get(
                "/api/auth/csrf-token", name="/api/auth/csrf-token"
            )

            if response.status_code == 200:
                data = response.json()
                self.csrf_token = data.get("data", {}).get("token")

            # 登录
            response = self.client.post(
                "/api/auth/login",
                json={
                    "username": f"user_{random.randint(1000, 9999)}",
                    "password": "password123",
                },
                headers={"X-CSRF-Token": self.csrf_token or ""},
                name="/api/auth/login",
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("data", {}).get("access_token")
                logger.info(f"User logged in: {self.auth_token[:20]}...")
            else:
                logger.warning(f"Login failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Login error: {e}")

    def logout(self):
        """登出"""
        try:
            self.client.post(
                "/api/auth/logout", headers=self._get_headers(), name="/api/auth/logout"
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")

    def _get_headers(self):
        """获取请求头"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        return headers

    @task(40)  # 权重40 - 最高频
    def query_realtime_data(self):
        """查询实时行情 - 最常见操作"""
        stock_code = random.choice(LoadTestConfig.STOCKS)

        self.client.get(
            f"/api/market/realtime/{stock_code}",
            headers=self._get_headers(),
            name="/api/market/realtime/[stock_code]",
        )

    @task(30)  # 权重30 - 次高频
    def query_kline_data(self):
        """查询K线数据"""
        stock_code = random.choice(LoadTestConfig.STOCKS)
        period = random.choice(["1", "5", "15", "30", "60", "D", "W"])

        self.client.get(
            f"/api/market/kline/{stock_code}",
            params={"period": period, "limit": random.choice([100, 200, 500])},
            headers=self._get_headers(),
            name="/api/market/kline/[stock_code]",
        )

    @task(20)  # 权重20
    def query_fund_flow(self):
        """查询资金流向"""
        stock_code = random.choice(LoadTestConfig.STOCKS)

        self.client.get(
            f"/api/market/fund-flow/{stock_code}",
            headers=self._get_headers(),
            name="/api/market/fund-flow/[stock_code]",
        )

    @task(15)  # 权重15
    def query_industry_fund_flow(self):
        """查询行业资金流向"""
        industry_type = random.choice(["csrc", "sw_l1"])

        if industry_type == "csrc":
            industry_code = random.choice(LoadTestConfig.INDUSTRIES_CSRC)
        else:
            industry_code = random.choice(LoadTestConfig.INDUSTRIES_SW_L1)

        self.client.get(
            "/api/market/v3/fund-flow",
            params={
                "industry_type": industry_type,
                "industry_code": industry_code,
                "limit": random.choice([5, 10, 20]),
            },
            headers=self._get_headers(),
            name="/api/market/v3/fund-flow",
        )

    @task(10)  # 权重10
    def search_stock(self):
        """搜索股票"""
        query = random.choice(["茅台", "农业银行", "招商银行", "中国石油"])

        self.client.get(
            "/api/search",
            params={"q": query, "limit": 10},
            headers=self._get_headers(),
            name="/api/search",
        )

    @task(8)
    def manage_watchlist(self):
        """管理自选股"""
        if random.random() < 0.5 and len(self.watchlist) < 10:
            # 添加到自选股
            stock_code = random.choice(LoadTestConfig.STOCKS)
            self.client.post(
                "/api/watchlist",
                json={"stock_code": stock_code},
                headers=self._get_headers(),
                name="/api/watchlist [POST]",
            )
            self.watchlist.append(stock_code)
        else:
            # 查询自选股
            self.client.get(
                "/api/watchlist",
                headers=self._get_headers(),
                name="/api/watchlist [GET]",
            )

    @task(5)
    def get_market_overview(self):
        """获取市场概览"""
        self.client.get(
            "/api/market/v2/overview",
            headers=self._get_headers(),
            name="/api/market/v2/overview",
        )

    @task(3)
    def query_alert_history(self):
        """查询告警历史 - Task 15集成"""
        self.client.get(
            "/api/alerts/history",
            params={"days": random.choice([1, 7, 30]), "limit": 100},
            headers=self._get_headers(),
            name="/api/alerts/history",
        )

    @task(2)
    def get_service_health(self):
        """获取服务健康度"""
        service = random.choice(["api", "database", "cache", "websocket"])

        self.client.get(
            f"/api/alerts/service-health/{service}",
            headers=self._get_headers(),
            name="/api/alerts/service-health/[service]",
        )

    @task(2)
    def health_check(self):
        """系统健康检查"""
        self.client.get("/health", name="/health")


class StockUser(HttpUser):
    """股票查询用户 - 模拟真实用户"""

    tasks = [StockBehaviors]
    wait_time = between(1, 3)  # 请求之间等待1-3秒

    def on_start(self):
        """用户连接时"""
        logger.info(f"User {self.client_id} started")

    def on_stop(self):
        """用户断开时"""
        logger.info(f"User {self.client_id} stopped")


class WebSocketBehaviors(TaskSet):
    """WebSocket行为集 - 实时行情订阅"""

    def on_start(self):
        """连接WebSocket"""
        import socketio

        self.sio = socketio.Client()
        self.connected = False

        try:
            self.sio.connect(LoadTestConfig.API_HOST, transports=["websocket"])
            self.connected = True
            logger.info(f"WebSocket connected: {self.parent.client_id}")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")

    def on_stop(self):
        """断开WebSocket"""
        if self.connected and self.sio:
            try:
                self.sio.disconnect()
                logger.info(f"WebSocket disconnected: {self.parent.client_id}")
            except Exception as e:
                logger.error(f"WebSocket disconnect error: {e}")

    @task(10)
    def subscribe_stock(self):
        """订阅股票行情"""
        if not self.connected:
            return

        try:
            stock_code = random.choice(LoadTestConfig.STOCKS)
            self.sio.emit("subscribe", {"stock_code": stock_code})
        except Exception as e:
            logger.error(f"Subscribe error: {e}")

    @task(5)
    def unsubscribe_stock(self):
        """取消订阅股票行情"""
        if not self.connected:
            return

        try:
            stock_code = random.choice(LoadTestConfig.STOCKS)
            self.sio.emit("unsubscribe", {"stock_code": stock_code})
        except Exception as e:
            logger.error(f"Unsubscribe error: {e}")


class WebSocketUser(HttpUser):
    """WebSocket实时用户"""

    tasks = [WebSocketBehaviors]
    wait_time = constant_pacing(5)  # 每5秒发送一条消息


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始"""
    logger.info("Load test started")
    logger.info(f"Target: {LoadTestConfig.API_HOST}")
    logger.info(f"Users: {LoadTestConfig.TARGET_USERS}")
    logger.info(f"Ramp-up: {LoadTestConfig.RAMP_UP_TIME}s")
    logger.info(f"Duration: {LoadTestConfig.TEST_DURATION}s")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束"""
    logger.info("Load test stopped")
    logger.info(f"Total requests: {environment.stats.total.num_requests}")
    logger.info(f"Failed requests: {environment.stats.total.num_failures}")
    logger.info(f"Response time avg: {environment.stats.total.avg_response_time:.0f}ms")
    logger.info(
        f"Response time p95: {environment.stats.total.get_response_time_percentile(0.95):.0f}ms"
    )
    logger.info(
        f"Response time p99: {environment.stats.total.get_response_time_percentile(0.99):.0f}ms"
    )


@events.request.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """请求成功回调"""
    if response_time > 1000:  # 超过1秒的请求记录
        logger.warning(f"Slow request: {name} - {response_time:.0f}ms")


@events.request_failure.add_listener
def on_request_failure(
    request_type, name, response_time, response_length, exception, **kwargs
):
    """请求失败回调"""
    logger.error(f"Request failed: {name} - {exception}")


if __name__ == "__main__":
    # 可以直接运行此脚本进行本地测试
    print(
        "Load test script ready. Use 'locust -f load_test_locustfile.py' to start testing"
    )
