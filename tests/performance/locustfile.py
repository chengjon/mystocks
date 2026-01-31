"""
Locust Performance Test Configuration
For API load testing and performance benchmarking
"""

from locust import HttpUser, between, events, task
from locust.runners import MasterRunner


class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(10)
    def market_overview(self):
        """Test market overview endpoint"""
        with self.client.get("/api/v1/market/overview", name="Market Overview", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(8)
    def stock_quote(self):
        """Test stock quote endpoint"""
        with self.client.get("/api/v1/stock/000001/quote", name="Stock Quote", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(5)
    def stock_kline(self):
        """Test stock K-line endpoint"""
        with self.client.get(
            "/api/v1/stock/000001/kline?period=day", name="Stock K-line", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(3)
    def fund_flow(self):
        """Test fund flow endpoint"""
        with self.client.get("/api/v1/market/fund-flow", name="Fund Flow", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(2)
    def dragon_tiger(self):
        """Test dragon tiger list endpoint"""
        with self.client.get("/api/v1/market/dragon-tiger", name="Dragon Tiger", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def portfolio(self):
        """Test portfolio endpoint"""
        with self.client.get("/api/v1/portfolio", name="Portfolio", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize custom metrics"""
    if isinstance(environment.runner, MasterRunner):
        environment.runner.register_message("stats", lambda msg: print(f"Custom stats: {msg.data}"))


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Handle test stop"""
    print("Performance test completed")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Failed requests: {environment.stats.total.num_failures}")
    print(f"Avg response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"P95 response time: {environment.stats.total.get_response_time_percentile(0.95):.2f}ms")
