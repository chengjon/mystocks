"""
Test Data Factory for E2E Tests
Provides factories for creating test data
"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class DataFactory:
    """测试数据工厂"""

    @staticmethod
    def generate_username() -> str:
        """生成测试用户名"""
        return f"test_user_{random.randint(1000, 9999)}"

    @staticmethod
    def generate_password() -> str:
        """生成测试密码"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return "".join(random.choices(chars, k=12))

    @staticmethod
    def generate_email(username: str = None) -> str:
        """生成测试邮箱"""
        username = username or DataFactory.generate_username()
        return f"{username}@test.example.com"

    @staticmethod
    def create_test_user(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建测试用户数据"""
        user = {
            "username": DataFactory.generate_username(),
            "password": DataFactory.generate_password(),
            "email": DataFactory.generate_email(),
            "phone": f"138{random.randint(10000000, 99999999)}",
            "balance": random.randint(10000, 1000000),
        }
        if overrides:
            user.update(overrides)
        return user

    @staticmethod
    def create_stock_data(code: str = None, name: str = None, days: int = 30) -> Dict[str, Any]:
        """创建股票数据"""
        base_price = random.uniform(10, 100)
        stock_code = code or f"{random.randint(0, 9):06d}"
        stock_name = name or f"股票{stock_code}"

        prices = []
        current_price = base_price
        for _ in range(days):
            change = random.uniform(-5, 5)
            current_price = max(current_price + change, 1)
            prices.append(round(current_price, 2))

        return {
            "code": stock_code,
            "name": stock_name,
            "prices": prices,
            "current_price": prices[-1],
            "change_percent": round((prices[-1] - prices[0]) / prices[0] * 100, 2),
        }

    @staticmethod
    def create_order_data(stock_code: str = None, quantity: int = None, price: float = None) -> Dict[str, Any]:
        """创建订单数据"""
        return {
            "stock_code": stock_code or f"{random.randint(0, 9):06d}",
            "stock_name": f"股票{stock_code or random.randint(0, 999):06d}",
            "order_type": random.choice(["buy", "sell"]),
            "quantity": quantity or random.randint(100, 10000),
            "price": price or round(random.uniform(10, 100), 2),
            "status": random.choice(["pending", "filled", "cancelled"]),
        }

    @staticmethod
    def create_portfolio_data(name: str = None) -> Dict[str, Any]:
        """创建投资组合数据"""
        return {
            "name": name or f"测试组合_{random.randint(100, 999)}",
            "initial_balance": random.randint(100000, 1000000),
            "current_balance": random.randint(100000, 1000000),
            "stocks": [
                {
                    "code": f"{random.randint(0, 9):06d}",
                    "quantity": random.randint(100, 10000),
                    "current_price": round(random.uniform(10, 100), 2),
                }
                for _ in range(random.randint(3, 10))
            ],
        }

    @staticmethod
    def create_backtest_config() -> Dict[str, Any]:
        """创建回测配置"""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()

        return {
            "strategy_type": random.choice(["ma", "rsi", "macd", "boll"]),
            "stock_code": f"{random.randint(0, 9):06d}",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "initial_capital": random.randint(100000, 1000000),
            "parameters": {
                "short_window": random.randint(5, 20),
                "long_window": random.randint(20, 60),
            },
        }

    @staticmethod
    def generate_ohlcv_data(days: int = 30) -> List[Dict[str, Any]]:
        """生成OHLCV数据"""
        data = []
        base_price = random.uniform(50, 200)
        current_date = datetime.now() - timedelta(days=days)

        for _ in range(days):
            open_price = base_price + random.uniform(-5, 5)
            close_price = open_price + random.uniform(-10, 10)
            high_price = max(open_price, close_price) + random.uniform(0, 5)
            low_price = min(open_price, close_price) - random.uniform(0, 5)
            volume = random.randint(1000000, 100000000)

            data.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                }
            )

            base_price = close_price
            current_date += timedelta(days=1)

        return data


class MarketDataFactory:
    """市场数据工厂"""

    @staticmethod
    def create_market_overview() -> Dict[str, Any]:
        """创建市场概览数据"""
        return {
            "indices": [
                {
                    "code": "000001",
                    "name": "上证指数",
                    "value": random.uniform(3000, 4000),
                    "change": random.uniform(-2, 2),
                },
                {
                    "code": "399001",
                    "name": "深证成指",
                    "value": random.uniform(10000, 15000),
                    "change": random.uniform(-2, 2),
                },
                {
                    "code": "399006",
                    "name": "创业板指",
                    "value": random.uniform(2000, 3000),
                    "change": random.uniform(-2, 2),
                },
            ],
            "total_stocks": random.randint(4000, 5000),
            "up_count": random.randint(1000, 3000),
            "down_count": random.randint(1000, 3000),
            "total_volume": random.randint(5000000000, 10000000000),
        }

    @staticmethod
    def create_fund_flow(days: int = 5) -> List[Dict[str, Any]]:
        """创建资金流向数据"""
        return [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "main_inflow": random.uniform(100000000, 500000000),
                "small_inflow": random.uniform(50000000, 200000000),
                "main_outflow": random.uniform(-500000000, -100000000),
            }
            for i in range(days)
        ]

    @staticmethod
    def create_dragon_tiger_list() -> List[Dict[str, Any]]:
        """创建龙虎榜数据"""
        return [
            {
                "stock_code": f"{random.randint(0, 9):06d}",
                "stock_name": f"股票{i}",
                "buy_amount": random.randint(10000000, 100000000),
                "sell_amount": random.randint(10000000, 100000000),
                "net_amount": random.randint(-50000000, 50000000),
                "buy_count": random.randint(100, 1000),
                "sell_count": random.randint(100, 1000),
            }
            for i in range(20)
        ]
