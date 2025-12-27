"""
Mock时序数据源实现

本模块实现ITimeSeriesDataSource接口的Mock版本，用于开发和测试。
使用faker库生成参数化的随机数据，支持灵活的数据生成。

核心特性:
1. 参数化数据生成 - 可控制数据量、时间范围
2. 真实数据模拟 - 价格、成交量等数据符合实际规律
3. 高性能 - 内存中生成，响应速度快
4. 完整接口实现 - 100%实现ITimeSeriesDataSource

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import random
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import pandas as pd
from faker import Faker

from src.interfaces.timeseries_data_source import ITimeSeriesDataSource


class MockTimeSeriesDataSource(ITimeSeriesDataSource):
    """
    Mock时序数据源实现

    用于开发测试环境，无需真实数据库连接。
    生成的数据符合实际市场规律，可用于前端开发和集成测试。
    """

    def __init__(self, seed: Optional[int] = None, locale: str = "zh_CN"):
        """
        初始化Mock数据源

        Args:
            seed: 随机种子，设置后每次生成相同数据（便于测试）
            locale: 语言区域，默认中文
        """
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        # 预定义股票池
        self._stock_pool = self._generate_stock_pool(100)

        # 预定义指数池
        self._index_pool = {
            "sh000001": {"name": "上证指数", "base_value": 3000.0},
            "sz399001": {"name": "深证成指", "base_value": 11000.0},
            "sz399006": {"name": "创业板指", "base_value": 2500.0},
            "sz399300": {"name": "沪深300", "base_value": 4000.0},
        }

    # ==================== 辅助方法 ====================

    def _generate_stock_pool(self, count: int) -> List[Dict[str, Any]]:
        """生成股票池"""
        stocks = []
        for i in range(count):
            # 生成股票代码
            if i % 2 == 0:
                symbol = f"6{str(i).zfill(5)}"  # 上海A股
            else:
                symbol = f"0{str(i).zfill(5)}"  # 深圳A股

            stocks.append(
                {
                    "symbol": symbol,
                    "name": self.fake.company(),
                    "base_price": round(random.uniform(5.0, 300.0), 2),
                }
            )
        return stocks

    def _get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基础信息"""
        for stock in self._stock_pool:
            if stock["symbol"] == symbol:
                return stock

        # 如果不在池中，动态生成
        return {
            "symbol": symbol,
            "name": self.fake.company(),
            "base_price": round(random.uniform(5.0, 300.0), 2),
        }

    def _generate_price_movement(self, base_price: float, volatility: float = 0.02) -> float:
        """
        生成价格波动

        Args:
            base_price: 基准价格
            volatility: 波动率 (默认2%)

        Returns:
            波动后的价格
        """
        change_percent = random.uniform(-volatility, volatility)
        return round(base_price * (1 + change_percent), 2)

    # ==================== 实时行情相关 ====================

    def get_realtime_quotes(
        self, symbols: Optional[List[str]] = None, fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取实时行情数据

        生成逻辑:
        - 价格基于base_price上下2%波动
        - 成交量在100万到1亿之间
        - 涨跌幅在-10%到+10%之间
        """
        # 确定查询的股票列表
        if symbols is None:
            # 返回前10只股票
            target_stocks = self._stock_pool[:10]
        else:
            target_stocks = [self._get_stock_info(s) for s in symbols]

        quotes = []
        for stock in target_stocks:
            base_price = stock["base_price"]

            # 生成当前价格
            price = self._generate_price_movement(base_price)

            # 生成涨跌
            pre_close = round(base_price * random.uniform(0.98, 1.02), 2)
            change = round(price - pre_close, 2)
            change_percent = round((change / pre_close) * 100, 2) if pre_close > 0 else 0

            # 生成成交量和成交额
            volume = random.randint(1000000, 100000000)
            amount = round(volume * price, 2)

            # 生成高低价
            high = round(max(price, pre_close) * random.uniform(1.0, 1.05), 2)
            low = round(min(price, pre_close) * random.uniform(0.95, 1.0), 2)
            open_price = round(random.uniform(low, high), 2)

            quote = {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "price": price,
                "change": change,
                "change_percent": change_percent,
                "volume": volume,
                "amount": amount,
                "high": high,
                "low": low,
                "open": open_price,
                "pre_close": pre_close,
                "bid1_price": round(price - 0.01, 2),
                "bid1_volume": random.randint(100, 10000),
                "ask1_price": round(price + 0.01, 2),
                "ask1_volume": random.randint(100, 10000),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # 如果指定了fields，只返回指定字段
            if fields:
                quote = {k: v for k, v in quote.items() if k in fields or k == "symbol"}

            quotes.append(quote)

        return quotes

    def get_kline_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        获取K线数据

        生成逻辑:
        - 根据interval生成对应数量的K线
        - 价格遵循随机游走模型
        - OHLC关系合理 (high >= close/open >= low)
        """
        stock_info = self._get_stock_info(symbol)
        base_price = stock_info["base_price"]

        # 计算K线数量
        time_delta = end_time - start_time
        if interval == "1d":
            num_bars = time_delta.days
            freq = "D"
        elif interval == "1w":
            num_bars = time_delta.days // 7
            freq = "W"
        elif interval == "1M":
            num_bars = time_delta.days // 30
            freq = "M"
        elif interval in ["1m", "5m", "15m", "30m", "60m"]:
            minutes = int(interval.replace("m", ""))
            num_bars = int(time_delta.total_seconds() / 60 / minutes)
            freq = f"{minutes}T"
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # 生成时间序列
        dates = pd.date_range(start=start_time, periods=min(num_bars, 1000), freq=freq)

        # 生成价格序列（随机游走）
        klines = []
        current_price = base_price

        for timestamp in dates:
            # 开盘价基于前一日收盘价波动
            open_price = self._generate_price_movement(current_price, 0.02)

            # 生成收盘价
            close_price = self._generate_price_movement(open_price, 0.03)

            # 生成最高价和最低价
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)

            # 生成成交量
            volume = random.randint(1000000, 50000000)
            amount = round(volume * close_price, 2)

            klines.append(
                {
                    "timestamp": timestamp,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                    "amount": amount,
                }
            )

            # 更新当前价格
            current_price = close_price

        return pd.DataFrame(klines)

    def get_intraday_chart(self, symbol: str, trade_date: Optional[date] = None) -> pd.DataFrame:
        """
        获取分时图数据

        生成逻辑:
        - 生成从9:30到15:00的分钟级数据
        - 价格围绕基准价格波动
        - 成交量和成交额累计增长
        """
        if trade_date is None:
            trade_date = date.today()

        stock_info = self._get_stock_info(symbol)
        base_price = stock_info["base_price"]

        # 生成分时数据 (9:30-11:30, 13:00-15:00)
        times = []

        # 上午时段
        current_time = datetime.combine(trade_date, datetime.min.time().replace(hour=9, minute=30))
        end_morning = datetime.combine(trade_date, datetime.min.time().replace(hour=11, minute=30))
        while current_time <= end_morning:
            times.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=1)

        # 下午时段
        current_time = datetime.combine(trade_date, datetime.min.time().replace(hour=13, minute=0))
        end_afternoon = datetime.combine(trade_date, datetime.min.time().replace(hour=15, minute=0))
        while current_time <= end_afternoon:
            times.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=1)

        # 生成价格数据
        intraday_data = []
        cumulative_volume = 0
        cumulative_amount = 0.0
        current_price = base_price

        for time_str in times:
            # 生成当前价格
            price = self._generate_price_movement(current_price, 0.005)

            # 计算均价
            minute_volume = random.randint(10000, 500000)
            minute_amount = round(minute_volume * price, 2)

            cumulative_volume += minute_volume
            cumulative_amount += minute_amount
            avg_price = round(cumulative_amount / cumulative_volume, 2) if cumulative_volume > 0 else price

            intraday_data.append(
                {
                    "time": time_str,
                    "price": round(price, 2),
                    "avg_price": avg_price,
                    "volume": cumulative_volume,
                    "amount": cumulative_amount,
                }
            )

            current_price = price

        return pd.DataFrame(intraday_data)

    def get_fund_flow(self, symbol: str, start_date: date, end_date: date, flow_type: str = "main") -> pd.DataFrame:
        """
        获取资金流向数据

        生成逻辑:
        - 主力资金净流入在-5亿到+5亿之间
        - 超大单、大单、中单、小单比例合理
        """
        stock_info = self._get_stock_info(symbol)
        base_price = stock_info["base_price"]

        # 生成日期序列
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")

        fund_flows = []
        for trade_date in date_range:
            # 生成主力净流入
            main_net_inflow = random.uniform(-500000000, 500000000)
            main_net_inflow_rate = round((main_net_inflow / (base_price * 100000000)) * 100, 2)

            # 生成各类资金净流入（超大单 + 大单 = 主力）
            super_net_inflow = main_net_inflow * random.uniform(0.4, 0.7)
            large_net_inflow = main_net_inflow - super_net_inflow

            # 中单和小单（加起来应该等于主力的相反数）
            medium_net_inflow = -main_net_inflow * random.uniform(0.3, 0.6)
            small_net_inflow = -main_net_inflow - medium_net_inflow

            fund_flows.append(
                {
                    "trade_date": trade_date.date(),
                    "main_net_inflow": round(main_net_inflow, 2),
                    "main_net_inflow_rate": main_net_inflow_rate,
                    "super_net_inflow": round(super_net_inflow, 2),
                    "large_net_inflow": round(large_net_inflow, 2),
                    "medium_net_inflow": round(medium_net_inflow, 2),
                    "small_net_inflow": round(small_net_inflow, 2),
                }
            )

        return pd.DataFrame(fund_flows)

    def get_top_fund_flow_stocks(
        self,
        trade_date: Optional[date] = None,
        flow_type: str = "main",
        direction: str = "inflow",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取资金流向排名

        生成逻辑:
        - 从股票池中随机选择limit只股票
        - 按资金净流入排序
        """
        if trade_date is None:
            trade_date = date.today()

        # 从股票池中选择股票
        selected_stocks = random.sample(self._stock_pool, min(limit, len(self._stock_pool)))

        rankings = []
        for rank, stock in enumerate(selected_stocks, 1):
            base_price = stock["base_price"]

            # 生成资金流向数据
            main_net_inflow = random.uniform(-300000000, 300000000)
            main_net_inflow_rate = round((main_net_inflow / (base_price * 100000000)) * 100, 2)

            # 生成涨跌幅
            change_percent = round(random.uniform(-10.0, 10.0), 2)

            rankings.append(
                {
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "trade_date": trade_date.isoformat(),
                    "main_net_inflow": round(main_net_inflow, 2),
                    "main_net_inflow_rate": main_net_inflow_rate,
                    "change_percent": change_percent,
                    "rank": rank,
                }
            )

        # 排序（净流入或净流出）
        if direction == "inflow":
            rankings.sort(key=lambda x: x["main_net_inflow"], reverse=True)
        else:
            rankings.sort(key=lambda x: x["main_net_inflow"])

        # 重新分配排名
        for rank, item in enumerate(rankings, 1):
            item["rank"] = rank

        return rankings[:limit]

    # ==================== 市场概览相关 ====================

    def get_market_overview(self, trade_date: Optional[date] = None) -> Dict[str, Any]:
        """
        获取市场概览数据

        生成逻辑:
        - 总股票数固定
        - 涨跌家数符合正态分布
        - 指数数据真实
        """
        if trade_date is None:
            trade_date = date.today()

        total_stocks = len(self._stock_pool)
        up_stocks = random.randint(int(total_stocks * 0.3), int(total_stocks * 0.7))
        down_stocks = random.randint(0, total_stocks - up_stocks)
        flat_stocks = total_stocks - up_stocks - down_stocks

        # 生成指数数据
        indices = {}
        for code, info in self._index_pool.items():
            base_value = info["base_value"]
            close_value = self._generate_price_movement(base_value, 0.02)
            change = round(close_value - base_value, 2)
            change_percent = round((change / base_value) * 100, 2)

            indices[code] = {
                "name": info["name"],
                "close": close_value,
                "change": change,
                "change_percent": change_percent,
            }

        return {
            "trade_date": trade_date.isoformat(),
            "total_stocks": total_stocks,
            "up_stocks": up_stocks,
            "down_stocks": down_stocks,
            "flat_stocks": flat_stocks,
            "limit_up_stocks": random.randint(0, 50),
            "limit_down_stocks": random.randint(0, 15),
            "total_volume": random.randint(400000000000, 600000000000),
            "total_amount": round(random.uniform(5000000000000, 7000000000000), 2),
            "avg_change_percent": round(random.uniform(-2.0, 2.0), 2),
            "indices": indices,
        }

    def get_index_realtime(self, index_codes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """获取指数实时数据"""
        if index_codes is None:
            index_codes = list(self._index_pool.keys())

        index_data = []
        for code in index_codes:
            if code not in self._index_pool:
                continue

            info = self._index_pool[code]
            base_value = info["base_value"]

            # 生成当前值
            close_value = self._generate_price_movement(base_value, 0.015)
            pre_close = round(base_value * random.uniform(0.99, 1.01), 2)
            change = round(close_value - pre_close, 2)
            change_percent = round((change / pre_close) * 100, 2)

            # 生成高低价
            high = round(max(close_value, pre_close) * 1.01, 2)
            low = round(min(close_value, pre_close) * 0.99, 2)
            open_value = round(random.uniform(low, high), 2)

            index_data.append(
                {
                    "code": code,
                    "name": info["name"],
                    "close": close_value,
                    "change": change,
                    "change_percent": change_percent,
                    "high": high,
                    "low": low,
                    "open": open_value,
                    "pre_close": pre_close,
                    "volume": random.randint(200000000000, 300000000000),
                    "amount": round(random.uniform(2500000000000, 3500000000000), 2),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return index_data

    # ==================== 技术指标相关 ====================

    def calculate_technical_indicators(
        self, symbol: str, start_date: date, end_date: date, indicators: List[str]
    ) -> pd.DataFrame:
        """
        计算技术指标

        生成逻辑:
        - 先生成K线数据
        - 基于K线计算各类技术指标
        """
        # 先获取K线数据
        kline_df = self.get_kline_data(
            symbol,
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time()),
            interval="1d",
        )

        # 添加技术指标列
        result_df = kline_df[["timestamp", "close"]].copy()
        result_df.columns = ["date", "close"]

        # 简化的技术指标计算（实际应使用ta-lib）
        if "MA5" in indicators or "MA" in indicators:
            result_df["MA5"] = result_df["close"].rolling(window=5).mean().round(2)

        if "MA10" in indicators or "MA" in indicators:
            result_df["MA10"] = result_df["close"].rolling(window=10).mean().round(2)

        if "MA20" in indicators or "MA" in indicators:
            result_df["MA20"] = result_df["close"].rolling(window=20).mean().round(2)

        # MACD (简化版)
        if "MACD" in indicators:
            ema12 = result_df["close"].ewm(span=12, adjust=False).mean()
            ema26 = result_df["close"].ewm(span=26, adjust=False).mean()
            result_df["MACD_DIF"] = (ema12 - ema26).round(2)
            result_df["MACD_DEA"] = result_df["MACD_DIF"].ewm(span=9, adjust=False).mean().round(2)
            result_df["MACD_MACD"] = ((result_df["MACD_DIF"] - result_df["MACD_DEA"]) * 2).round(2)

        return result_df

    # ==================== 竞价和盘口相关 ====================

    def get_auction_data(
        self,
        trade_date: Optional[date] = None,
        auction_type: str = "open",
        min_amount: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取竞价抢筹数据"""
        if trade_date is None:
            trade_date = date.today()

        selected_stocks = random.sample(self._stock_pool, min(limit, len(self._stock_pool)))

        auction_data = []
        for stock in selected_stocks:
            base_price = stock["base_price"]

            # 生成竞价价格和成交量
            auction_price = round(base_price * random.uniform(0.95, 1.05), 2)
            auction_volume = random.randint(100000, 5000000)
            auction_amount = round(auction_volume * auction_price, 2)

            # 过滤最小金额
            if min_amount and auction_amount < min_amount:
                continue

            auction_data.append(
                {
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "trade_date": trade_date.isoformat(),
                    "auction_type": auction_type,
                    "auction_price": auction_price,
                    "auction_volume": auction_volume,
                    "auction_amount": auction_amount,
                    "change_percent": round(random.uniform(-5.0, 5.0), 2),
                }
            )

        # 按成交额排序
        auction_data.sort(key=lambda x: x["auction_amount"], reverse=True)

        return auction_data[:limit]

    # ==================== 数据质量和健康检查 ====================

    def check_data_quality(self, symbol: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """检查时序数据质量"""
        # Mock数据质量总是很好
        total_days = (end_date - start_date).days

        return {
            "symbol": symbol,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_records": total_days,
            "missing_records": random.randint(0, 3),
            "completeness_rate": round(random.uniform(96.0, 100.0), 2),
            "data_freshness": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quality_score": round(random.uniform(92.0, 100.0), 2),
            "issues": [],
        }

    def health_check(self) -> Dict[str, Any]:
        """时序数据源健康检查"""
        return {
            "status": "healthy",
            "data_source_type": "mock",
            "response_time_ms": random.randint(1, 10),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "connection_status": "connected",
            "metrics": {
                "total_queries_today": random.randint(1000, 50000),
                "avg_response_time_ms": random.randint(5, 50),
                "error_rate_percent": round(random.uniform(0.0, 0.1), 2),
            },
        }
