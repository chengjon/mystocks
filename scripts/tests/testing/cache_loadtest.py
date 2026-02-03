from locust import HttpUser, task, between
import random

class CacheUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时的初始化"""
        pass

    @task(3)
    def get_market_data(self):
        """获取市场数据（高频操作）"""
        symbols = ['000001', '000002', '600000', '600519', '000858', '601318', '601166', '000725']
        symbol = random.choice(symbols)
        self.client.get(f"/api/market/quotes?symbols={symbol}")

    @task(2)
    def get_kline_data(self):
        """获取 K 线数据"""
        self.client.get("/api/market/kline?symbol=000001&interval=1d&limit=100")

    @task(1)
    def get_health(self):
        """健康检查"""
        self.client.get("/health")

    @task(1)
    def get_metrics(self):
        """获取指标"""
        self.client.get("/metrics")
