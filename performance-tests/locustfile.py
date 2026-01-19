"""
MyStocks量化平台API压力测试
基于Locust实现的性能测试套件

目标:
- 模拟10个并发用户
- 测试API响应时间和吞吐量
- 验证系统在高负载下的稳定性

运行方式:
locust -f /opt/claude/mystocks_spec/performance-tests/locustfile.py --host=http://localhost:8000
"""

import os
import random
import time
from datetime import datetime
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner

# 测试配置
API_HOST = "http://localhost:8000"
STOCKS = [
    "000001", "000002", "600000", "600036", "000858",
    "601398", "601939", "600519", "000333", "000651"
]

class MyStocksUser(HttpUser):
    """MyStocks API用户模拟"""

    wait_time = between(1, 3)  # 请求间隔1-3秒

    def on_start(self):
        """用户启动时的初始化"""
        self.auth_token = None

    @task(4)
    def get_market_overview(self):
        """获取市场概览数据 - 高频操作"""
        with self.client.get("/api/market/overview",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"市场概览API失败: {response.status_code}")

    @task(3)
    def get_stock_quotes(self):
        """获取股票实时报价"""
        symbol = random.choice(STOCKS)
        with self.client.get(f"/api/market/quote/{symbol}",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"股票报价API失败: {response.status_code}")

    @task(3)
    def get_daily_kline(self):
        """获取日K线数据"""
        symbol = random.choice(STOCKS)
        with self.client.get(f"/api/market/daily-kline/{symbol}?limit=100",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"日K线API失败: {response.status_code}")

    @task(2)
    def get_technical_indicators(self):
        """获取技术指标"""
        symbol = random.choice(STOCKS)
        with self.client.get(f"/api/technical/{symbol}/indicators",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"技术指标API失败: {response.status_code}")

    @task(2)
    def get_strategy_list(self):
        """获取策略列表"""
        with self.client.get("/api/strategies",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"策略列表API失败: {response.status_code}")

    @task(1)
    def health_check(self):
        """健康检查"""
        with self.client.get("/api/health",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"健康检查失败: {response.status_code}")


# 性能监控钩子
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的处理"""
    print(f"🚀 开始性能测试 - 目标: {environment.runner.user_count} 用户")
    print(f"📊 测试配置: {environment.runner.spawn_rate} 用户/秒孵化率")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时的处理"""
    print("✅ 性能测试完成")

@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    """用户孵化完成时的处理"""
    print(f"🎯 已孵化 {user_count} 个用户，开始执行测试")

@events.request_success.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """请求成功时的处理"""
    if response_time > 1000:  # 超过1秒的请求
        print(f"⚠️  慢请求: {name} - {response_time}ms")

@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, exception, **kwargs):
    """请求失败时的处理"""
    print(f"❌ 请求失败: {name} - {exception}")
