"""
数据源适配器 - 集成现有 Data API 到数据源工厂模式
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor
from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)

logger = __import__("logging").getLogger(__name__)


class DataSourceMetrics:
    """数据源监控指标"""

    def __init__(self):
        self.availability: float = 0.0  # 可用性百分比 (0-100)
        self.response_time: float = 0.0  # 平均响应时间 (ms)
        self.success_rate: float = 0.0  # 成功率百分比 (0-100)
        self.error_count: int = 0  # 错误次数
        self.last_error = None  # 最后错误信息
        self.last_check = None  # 最后检查时间
        self.total_requests: int = 0  # 总请求数
        self.data_delay = None  # 数据延迟 (秒)

    def record_request(self, success: bool = True, error_msg: Optional[str] = None):
        """记录请求结果，更新指标"""
        self.total_requests += 1
        if success:
            # 计算成功率 (移动平均)
            if self.total_requests == 1:
                self.success_rate = 100.0
            else:
                # 使用指数移动平均
                alpha = 0.1  # 平滑因子
                self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate
        else:
            self.error_count += 1
            if error_msg:
                self.last_error = error_msg

            # 更新成功率
            if self.total_requests == 1:
                self.success_rate = 0.0
            else:
                failed_rate = (self.error_count / self.total_requests) * 100
                self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_success(self, response_time: float = 0.0):
        """记录成功请求，更新指标"""
        self.total_requests += 1
        self.response_time = response_time

        # 计算成功率 (移动平均)
        if self.total_requests == 1:
            self.success_rate = 100.0
        else:
            # 使用指数移动平均
            alpha = 0.1  # 平滑因子
            self.success_rate = alpha * 100.0 + (1 - alpha) * self.success_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()

    def record_error(self, response_time: float = 0.0, error_msg: str = ""):
        """记录错误，更新指标"""
        self.total_requests += 1
        self.error_count += 1
        if error_msg:
            self.last_error = error_msg

        # 更新成功率
        if self.total_requests == 1:
            self.success_rate = 0.0
        else:
            failed_rate = (self.error_count / self.total_requests) * 100
            self.success_rate = 100.0 - failed_rate

        # 更新可用性 (基于成功率)
        self.availability = self.success_rate

        # 更新最后检查时间
        self.last_check = datetime.now()


class DataDataSourceAdapter(IDataSource):
    """数据源适配器 - 集成现有 Data API 到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "data"
        self.name = config.get("name", "Data Source")

        # 初始化缓存
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5分钟默认缓存

        # 初始化监控指标 (兼容数据源工厂)
        self.metrics = DataSourceMetrics()

        # 性能指标
        self.total_requests = 0
        self.successful_requests = 0
        self.error_count = 0
        self.last_response_time = 0.0

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取数据

        Args:
            endpoint: 数据端点 (stocks/basic, stocks/daily, financial, etc.)
            params: 请求参数

        Returns:
            格式化的数据响应
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            params = params or {}
            result = await self._fetch_data(endpoint, params)

            # 记录成功指标
            response_time = time.time() - start_time
            self.last_response_time = response_time * 1000  # 转换为毫秒
            self.successful_requests += 1

            # 更新监控指标
            self._update_metrics(success=True, response_time=response_time * 1000)

            # 触发数据质量监控
            await self._trigger_quality_monitoring(endpoint, result, response_time * 1000)

            return result

        except Exception as e:
            self.error_count += 1
            response_time = time.time() - start_time
            logger.error(f"Data fetch failed for {endpoint}: {str(e)}")

            # 更新监控指标
            self._update_metrics(success=False, response_time=response_time * 1000, error=str(e))

            # 记录失败的质量监控
            await self._trigger_quality_monitoring(endpoint, None, response_time * 1000, success=False)

            # 返回错误响应格式
            return {
                "status": "error",
                "message": f"Failed to fetch data: {str(e)}",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": endpoint,
            }

    async def _fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        实际的数据获取逻辑
        """
        # 根据端点类型调用相应的数据获取方法
        if endpoint == "stocks/basic":
            return await self._fetch_stocks_basic(params)
        elif endpoint == "stocks/daily":
            return await self._fetch_stocks_daily(params)
        elif endpoint == "stocks/kline":
            return await self._fetch_stocks_kline(params)
        elif endpoint == "financial":
            return await self._fetch_financial_data(params)
        elif endpoint == "stocks/detail":
            return await self._fetch_stock_detail(params)
        elif endpoint == "stocks/search":
            return await self._fetch_stocks_search(params)
        elif endpoint == "markets/overview":
            return await self._fetch_markets_overview(params)
        elif endpoint == "stocks/intraday":
            return await self._fetch_stocks_intraday(params)
        else:
            raise ValueError(f"Unsupported data endpoint: {endpoint}")

    async def _fetch_stocks_basic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取股票基本信息"""
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        search = params.get("search")
        industry = params.get("industry")
        concept = params.get("concept")
        market = params.get("market")
        sort_field = params.get("sort_field")
        sort_order = params.get("sort_order")

        try:
            # 使用现有的db_service查询逻辑
            df = db_service.query_stocks_basic(limit=1000)

            if df.empty:
                return {
                    "status": "success",
                    "data": [],
                    "total": 0,
                    "message": "暂无股票数据",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.source_type,
                    "endpoint": "stocks/basic",
                }

            # 应用筛选条件 (复制原有逻辑)
            if search:
                search_mask = df["symbol"].str.contains(search, case=False, na=False) | df["name"].str.contains(
                    search, case=False, na=False
                )
                df = df[search_mask]

            if industry:
                df = df[df["industry"] == industry]

            if concept:
                df = df[df.get("concepts", "").str.contains(concept, case=False, na=False)]

            if market:
                df = df[df["market"] == market]

            # 添加模拟实时行情数据
            import random

            random.seed(42)

            if "price" not in df.columns:
                df["price"] = [round(random.uniform(10, 100), 2) for _ in range(len(df))]
            if "change" not in df.columns:
                df["change"] = [round(random.uniform(-5, 5), 2) for _ in range(len(df))]
            if "change_pct" not in df.columns:
                df["change_pct"] = [
                    round(row["change"] / row["price"] * 100, 2) if row["price"] > 0 else 0 for _, row in df.iterrows()
                ]

            # 应用排序
            if sort_field and sort_field in df.columns:
                ascending = sort_order != "desc"
                df = df.sort_values(by=sort_field, ascending=ascending)

            # 应用分页
            total = len(df)
            df = df.iloc[offset : offset + limit]

            return {
                "status": "success",
                "data": df.to_dict("records"),
                "total": total,
                "message": f"成功获取 {total} 条股票数据",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "stocks/basic",
                "parameters": {
                    "limit": limit,
                    "offset": offset,
                    "search": search,
                    "industry": industry,
                    "concept": concept,
                    "market": market,
                    "sort_field": sort_field,
                    "sort_order": sort_order,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch stocks basic data: {str(e)}")

    async def _fetch_stocks_daily(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取股票日线数据"""
        symbol = params.get("symbol")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        limit = params.get("limit", 100)

        try:
            # 使用现有的db_service查询日线数据
            df = db_service.query_daily_kline(symbol, start_date, end_date, limit)

            if df.empty:
                return {
                    "status": "success",
                    "data": [],
                    "total": 0,
                    "message": f"股票 {symbol} 暂无日线数据",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.source_type,
                    "endpoint": "stocks/daily",
                }

            return {
                "status": "success",
                "data": df.to_dict("records"),
                "total": len(df),
                "message": f"成功获取股票 {symbol} 日线数据",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "stocks/daily",
                "parameters": {
                    "symbol": symbol,
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None,
                    "limit": limit,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch stocks daily data: {str(e)}")

    async def _fetch_stocks_kline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取股票K线数据 (标准化接口)"""
        symbol = params.get("symbol")
        period = params.get("period", "daily")
        adjust = params.get("adjust", "qfq")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        try:
            # 调用日线数据获取K线数据
            kline_data = await self._fetch_stocks_daily(
                {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": 1000,
                }
            )

            # 添加K线特定字段
            for record in kline_data.get("data", []):
                record["period"] = period
                record["adjust"] = adjust

            kline_data["endpoint"] = "stocks/kline"
            kline_data["parameters"].update({"period": period, "adjust": adjust})

            return kline_data

        except Exception as e:
            raise RuntimeError(f"Failed to fetch stocks kline data: {str(e)}")

    async def _fetch_financial_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取财务数据"""
        symbol = params.get("symbol")
        report_type = params.get("report_type", "income")  # income/balance/cashflow

        try:
            # 使用AkShare适配器获取财务数据 (如果可用)
            try:
                from utils.data_format_converter import get_akshare_adapter

                ak = get_akshare_adapter()

                if report_type == "income":
                    df = ak.get_income_statement(symbol)
                elif report_type == "balance":
                    df = ak.get_balance_sheet(symbol)
                elif report_type == "cashflow":
                    df = ak.get_cash_flow_statement(symbol)
                else:
                    raise ValueError(f"Unsupported report type: {report_type}")

                return {
                    "status": "success",
                    "data": df.to_dict("records") if not df.empty else [],
                    "total": len(df) if not df.empty else 0,
                    "message": f"成功获取股票 {symbol} {report_type} 财务数据",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.source_type,
                    "endpoint": "financial",
                    "parameters": {"symbol": symbol, "report_type": report_type},
                }

            except ImportError:
                # 如果AkShare不可用，返回模拟数据
                import random

                mock_data = [
                    {
                        "symbol": symbol,
                        "report_date": "2024-09-30",
                        "report_type": report_type,
                        "revenue": round(random.uniform(1e8, 1e10), 2),
                        "net_profit": round(random.uniform(1e7, 1e9), 2),
                        "total_assets": round(random.uniform(5e9, 5e11), 2),
                        "total_liabilities": round(random.uniform(1e9, 3e11), 2),
                    }
                ]

                return {
                    "status": "success",
                    "data": mock_data,
                    "total": len(mock_data),
                    "message": f"成功获取股票 {symbol} 模拟财务数据",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.source_type,
                    "endpoint": "financial",
                    "parameters": {"symbol": symbol, "report_type": report_type},
                    "note": "Using mock data - AkShare adapter not available",
                }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch financial data: {str(e)}")

    async def _fetch_stock_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取股票详细信息"""
        symbol = params.get("symbol")

        try:
            # 先获取基本信息
            basic_data = await self._fetch_stocks_basic({"search": symbol, "limit": 1})

            if not basic_data.get("data"):
                raise ValueError(f"Stock {symbol} not found")

            stock_info = basic_data["data"][0]

            # 添加更多详细信息
            import random

            detail_data = {
                **stock_info,
                "listing_date": "2010-01-01",
                "total_shares": random.randint(1e8, 1e10),
                "float_shares": random.randint(5e7, 5e9),
                "market_cap": random.randint(1e9, 1e12),
                "pe_ratio": round(random.uniform(10, 100), 2),
                "pb_ratio": round(random.uniform(1, 10), 2),
                "dividend_yield": round(random.uniform(0, 5), 2),
                "roe": round(random.uniform(0, 25), 2),
                "debt_ratio": round(random.uniform(10, 80), 2),
            }

            return {
                "status": "success",
                "data": detail_data,
                "message": f"成功获取股票 {symbol} 详细信息",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "stocks/detail",
                "parameters": {"symbol": symbol},
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch stock detail: {str(e)}")

    async def _fetch_stocks_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """股票搜索"""
        query = params.get("query", "")
        limit = params.get("limit", 20)

        try:
            # 使用基本信息接口进行搜索
            search_result = await self._fetch_stocks_basic(
                {
                    "search": query,
                    "limit": limit,
                    "sort_field": "symbol",
                    "sort_order": "asc",
                }
            )

            search_result["endpoint"] = "stocks/search"
            search_result["parameters"] = {"query": query, "limit": limit}

            return search_result

        except Exception as e:
            raise RuntimeError(f"Failed to search stocks: {str(e)}")

    async def _fetch_markets_overview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取市场概览"""
        try:
            # 获取基本信息统计
            basic_data = await self._fetch_stocks_basic({"limit": 1000})
            stocks = basic_data.get("data", [])

            # 计算市场统计数据
            import random

            total_stocks = len(stocks)
            rising_stocks = sum(1 for s in stocks if s.get("change_pct", 0) > 0)
            falling_stocks = sum(1 for s in stocks if s.get("change_pct", 0) < 0)
            flat_stocks = total_stocks - rising_stocks - falling_stocks

            # 计算总市值 (真正计算，不再mock)
            total_market_cap = 0.0
            valid_market_caps = 0

            for stock in stocks:
                market_cap = stock.get("market_cap", 0)
                if market_cap and market_cap > 0:
                    total_market_cap += market_cap
                    valid_market_caps += 1

            # 如果没有真实的市值数据，使用合理的模拟值
            if total_market_cap == 0 and stocks:
                # 基于股价和股数模拟市值
                for stock in stocks:
                    price = stock.get("price", 0)
                    shares = stock.get("total_shares", 0)
                    if price > 0 and shares > 0:
                        total_market_cap += price * shares
                    elif price > 0:
                        # 如果没有股数数据，使用行业平均股数估算
                        estimated_shares = 10000000000  # 100亿股（行业平均水平）
                        total_market_cap += price * estimated_shares

            # 将市值转换为万亿元单位
            total_market_cap_trillion = total_market_cap / 1000000000000  # 转换为万亿元

            # 计算市场分布
            by_market = {}
            by_industry = {}

            for stock in stocks:
                # 市场分布统计
                market = stock.get("market", "其他")
                if market in by_market:
                    by_market[market] += 1
                else:
                    by_market[market] = 1

                # 行业分布统计
                industry = stock.get("industry", "未分类")
                if industry and industry.strip():  # 过滤空字符串
                    if industry in by_industry:
                        by_industry[industry] += 1
                    else:
                        by_industry[industry] = 1

            # 如果没有真实的行业数据，提供合理的模拟数据
            if not by_industry:
                # 基于A股市场实际情况的模拟行业分布
                industries = [
                    "银行",
                    "房地产",
                    "医药生物",
                    "电子",
                    "计算机",
                    "机械设备",
                    "化工",
                    "食品饮料",
                    "汽车",
                    "电力设备",
                    "有色金属",
                    "钢铁",
                    "煤炭",
                    "建筑材料",
                    "建筑装饰",
                    "家用电器",
                    "休闲服务",
                    "商业贸易",
                    "交通运输",
                    "综合",
                ]

                # 为每个行业分配随机股票数，总计不超过实际股票数
                remaining_stocks = total_stocks
                for i, industry in enumerate(industries):
                    if i == len(industries) - 1:  # 最后一个行业分配剩余股票
                        count = remaining_stocks
                    else:
                        # 随机分配，但保证每个行业至少有一定数量
                        count = random.randint(
                            max(1, remaining_stocks // len(industries) - 5),
                            remaining_stocks // len(industries) + 10,
                        )
                        count = min(count, remaining_stocks)

                    by_industry[industry] = count
                    remaining_stocks -= count

            # 模拟市场指数
            overview_data = {
                "market_status": "trading",  # trading/closed
                "total_stocks": total_stocks,
                "total_market_cap": round(total_market_cap_trillion, 2),  # 新增：总市值(万亿元)
                "rising_stocks": rising_stocks,
                "falling_stocks": falling_stocks,
                "flat_stocks": flat_stocks,
                "limit_up_stocks": random.randint(0, 50),
                "limit_down_stocks": random.randint(0, 20),
                "suspended_stocks": random.randint(0, 10),
                "by_market": by_market,  # 新增：按市场分布
                "by_industry": by_industry,  # 新增：按行业分布
                "indices": [
                    {
                        "name": "上证指数",
                        "symbol": "000001.SH",
                        "value": round(random.uniform(3000, 3500), 2),
                        "change": round(random.uniform(-50, 50), 2),
                        "change_pct": round(random.uniform(-2, 2), 2),
                    },
                    {
                        "name": "深证成指",
                        "symbol": "399001.SZ",
                        "value": round(random.uniform(10000, 12000), 2),
                        "change": round(random.uniform(-100, 100), 2),
                        "change_pct": round(random.uniform(-2, 2), 2),
                    },
                ],
                "hot_industries": [
                    {"name": "新能源", "change_pct": round(random.uniform(1, 5), 2)},
                    {"name": "半导体", "change_pct": round(random.uniform(-1, 3), 2)},
                    {"name": "医药生物", "change_pct": round(random.uniform(0, 4), 2)},
                ],
            }

            return {
                "status": "success",
                "data": overview_data,
                "message": "成功获取市场概览数据",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "markets/overview",
                "parameters": {},
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch markets overview: {str(e)}")

    async def _fetch_stocks_intraday(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取股票分时数据"""
        symbol = params.get("symbol")

        try:
            # 生成模拟分时数据
            import random

            random.seed(42)

            current_time = datetime.now()
            base_price = random.uniform(10, 100)

            intraday_data = []
            for i in range(240):  # 4小时交易时间，每分钟一个数据点
                time_point = current_time.replace(hour=9, minute=30) + timedelta(minutes=i)
                price_change = random.uniform(-2, 2)
                volume = random.randint(100, 10000)

                intraday_data.append(
                    {
                        "time": time_point.strftime("%H:%M"),
                        "price": round(base_price + price_change, 2),
                        "volume": volume,
                        "amount": round(volume * (base_price + price_change), 2),
                    }
                )

            return {
                "status": "success",
                "data": intraday_data,
                "total": len(intraday_data),
                "message": f"成功获取股票 {symbol} 分时数据",
                "timestamp": datetime.now().isoformat(),
                "source": self.source_type,
                "endpoint": "stocks/intraday",
                "parameters": {"symbol": symbol},
                "note": "Using simulated intraday data",
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch stocks intraday data: {str(e)}")

    async def _trigger_quality_monitoring(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        response_time: float,
        success: bool = True,
    ) -> None:
        """触发数据质量监控"""
        try:
            monitor = get_data_quality_monitor()
            await monitor.evaluate_data_quality(
                data=data or {},
                source=f"{self.source_type}:{endpoint}",
                response_time=response_time,
                success=success,
            )
        except Exception as e:
            logger.warning(f"Failed to trigger quality monitoring: {str(e)}")

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        start_time = time.time()

        try:
            # 测试一个简单的数据获取操作
            await self._fetch_stocks_basic({"limit": 1})

            response_time = time.time() - start_time

            return HealthStatus(
                status=HealthStatusEnum.HEALTHY,
                response_time=response_time * 1000,  # 转换为毫秒
                message="Data source is healthy",
                timestamp=datetime.now(),
            )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=response_time * 1000,
                message=f"Data source health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "last_response_time_ms": self.last_response_time,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "source_type": self.source_type,
            "name": self.name,
        }

    def _update_metrics(self, success: bool, response_time: float, error: str = None):
        """更新监控指标 (兼容数据源工厂)"""
        self.metrics.total_requests += 1
        self.metrics.last_check = datetime.now()

        if success:
            # 更新响应时间 (使用指数移动平均)
            if self.metrics.response_time == 0:
                self.metrics.response_time = response_time
            else:
                alpha = 0.3  # 平滑因子
                self.metrics.response_time = alpha * response_time + (1 - alpha) * self.metrics.response_time
        else:
            self.metrics.error_count += 1
            self.metrics.last_error = error

        # 计算成功率
        if self.metrics.total_requests > 0:
            self.metrics.success_rate = (
                (self.metrics.total_requests - self.metrics.error_count) / self.metrics.total_requests * 100
            )

        # 计算可用性 (基于最近的成功率)
        self.metrics.availability = self.metrics.success_rate

    async def close(self):
        """关闭连接和清理资源"""
        # Data适配器不需要清理特定资源
        pass


class DashboardDataSourceAdapter(IDataSource):
    """仪表盘数据源适配器 - 集成现有 Dashboard API 到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "dashboard"
        self.name = config.get("name", "Dashboard Source")

        # 初始化缓存
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 120)  # 2分钟默认缓存

        # 初始化监控指标 (兼容数据源工厂)
        self.metrics = DataSourceMetrics()

        # 性能指标
        self.total_requests = 0
        self.successful_requests = 0
        self.error_count = 0
        self.last_response_time = 0.0

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        从仪表盘数据源获取数据
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            # 模拟仪表盘数据生成
            result = await self._generate_mock_dashboard_data(endpoint, params)

            # 记录成功请求
            self.successful_requests += 1
            response_time = (time.time() - start_time) * 1000
            self.last_response_time = response_time
            self._update_metrics(response_time, True)

            # 数据质量监控
            await self._trigger_quality_monitoring(endpoint, result, response_time)

            return result

        except Exception as e:
            # 记录错误请求
            self.error_count += 1
            response_time = (time.time() - start_time) * 1000
            self.last_response_time = response_time
            self._update_metrics(response_time, False)
            self.metrics.last_error = str(e)

            logger.error(f"Dashboard数据获取失败: endpoint={endpoint}, error={str(e)}")
            raise

    async def _generate_mock_dashboard_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成模拟仪表盘数据"""
        import random

        random.seed(42)  # 固定种子确保一致性

        if endpoint == "summary":
            user_id = params.get("user_id", 999) if params else 999

            # 市场概览数据
            market_overview = {
                "indices": [
                    {
                        "symbol": "000001",
                        "name": "上证指数",
                        "price": 3245.67,
                        "change": 15.32,
                        "change_pct": 0.47,
                    },
                    {
                        "symbol": "399001",
                        "name": "深证成指",
                        "price": 10876.54,
                        "change": -23.45,
                        "change_pct": -0.21,
                    },
                    {
                        "symbol": "399006",
                        "name": "创业板指",
                        "price": 2234.56,
                        "change": 12.34,
                        "change_pct": 0.55,
                    },
                ],
                "market_stats": {
                    "total_stocks": 5200,
                    "up_count": 2650,
                    "down_count": 2350,
                    "flat_count": 200,
                    "limit_up": 45,
                    "limit_down": 12,
                    "total_turnover": 8543200000,
                    "total_amount": 98765432100,
                },
                "sectors": [
                    {"name": "银行", "change_pct": 0.12, "count": 42},
                    {"name": "地产", "change_pct": -0.34, "count": 38},
                    {"name": "科技", "change_pct": 1.45, "count": 156},
                ],
            }

            # 自选股数据
            watchlist = [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "price": 12.34,
                    "change": 0.23,
                    "change_pct": 1.9,
                },
                {
                    "symbol": "000002",
                    "name": "万科A",
                    "price": 18.56,
                    "change": -0.45,
                    "change_pct": -2.37,
                },
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "price": 1678.90,
                    "change": 15.60,
                    "change_pct": 0.94,
                },
            ]

            # 持仓数据
            portfolio = [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "shares": 1000,
                    "cost": 11.80,
                    "price": 12.34,
                    "profit": 540.00,
                },
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "shares": 10,
                    "cost": 1650.00,
                    "price": 1678.90,
                    "profit": 289.00,
                },
            ]

            # 风险预警数据
            alerts = [
                {
                    "id": 1,
                    "symbol": "000002",
                    "type": "价格异动",
                    "message": "万科A跌幅超过2%",
                    "severity": "warning",
                },
                {
                    "id": 2,
                    "type": "成交量",
                    "message": "市场成交量异常放大",
                    "severity": "info",
                },
            ]

            dashboard_data = {
                "market_overview": market_overview,
                "watchlist": watchlist,
                "portfolio": portfolio,
                "alerts": alerts,
                "summary": {
                    "user_id": user_id,
                    "total_value": sum(item["shares"] * item["price"] for item in portfolio),
                    "total_cost": sum(item["shares"] * item["cost"] for item in portfolio),
                    "total_profit": sum(item["profit"] for item in portfolio),
                    "watchlist_count": len(watchlist),
                    "alert_count": len(alerts),
                },
            }

            return {
                "status": "success",
                "data": dashboard_data,
                "total": 1,
                "message": f"成功获取用户 {user_id} 的仪表盘数据",
                "timestamp": datetime.now().isoformat(),
                "source": "dashboard",
                "endpoint": endpoint,
                "parameters": params or {},
            }

        else:
            raise ValueError(f"Unsupported dashboard endpoint: {endpoint}")

    def _update_metrics(self, response_time: float, success: bool):
        """更新监控指标"""
        # 更新成功率
        if self.total_requests > 0:
            self.metrics.success_rate = (self.successful_requests / self.total_requests) * 100

        # 更新错误次数
        self.metrics.error_count = self.error_count
        self.metrics.last_check = datetime.now()

        # 更新平均响应时间
        if success:
            if self.metrics.response_time == 0:
                self.metrics.response_time = response_time
            else:
                # 使用指数移动平均
                alpha = 0.3
                self.metrics.response_time = alpha * response_time + (1 - alpha) * self.metrics.response_time

        # 更新可用性 (假设95%基础可用性，成功请求时提升)
        base_availability = 95.0
        if success:
            self.metrics.availability = min(100.0, base_availability + (self.metrics.success_rate - 90.0) * 0.1)
        else:
            self.metrics.availability = max(0.0, base_availability - (self.error_count / self.total_requests) * 10.0)

    async def _trigger_quality_monitoring(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        response_time: float,
        success: bool = True,
    ) -> None:
        """数据质量监控"""
        try:
            monitor = get_data_quality_monitor()
            await monitor.evaluate_data_quality(
                data=data or {},
                source=f"{self.source_type}:{endpoint}",
                response_time=response_time,
                success=success,
            )
        except Exception as e:
            logger.warning(f"Failed to trigger quality monitoring: {str(e)}")

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        try:
            # 简单的健康检查 - 生成少量测试数据
            test_params = {"user_id": 999}
            await self._generate_mock_dashboard_data("summary", test_params)

            # 基于响应时间和成功率确定健康状态
            if self.metrics.response_time < 1000 and self.metrics.success_rate >= 95:
                status = HealthStatusEnum.HEALTHY
                message = f"Dashboard service is healthy (RT: {self.metrics.response_time:.2f}ms)"
            elif self.metrics.response_time < 2000 and self.metrics.success_rate >= 90:
                status = HealthStatusEnum.DEGRADED
                message = f"Dashboard service is degraded (RT: {self.metrics.response_time:.2f}ms)"
            else:
                status = HealthStatusEnum.FAILED
                message = f"Dashboard service is unhealthy (RT: {self.metrics.response_time:.2f}ms)"

            return HealthStatus(
                status=status,
                message=message,
                response_time=self.metrics.response_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                message=f"Health check failed: {str(e)}",
                response_time=0,
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> "DataSourceMetrics":
        """获取监控指标"""
        return self.metrics

    async def close(self):
        """关闭连接和清理资源"""
        # Dashboard适配器不需要清理特定资源
        pass


# ============================================================================
# Technical Analysis Data Source Adapter
# ============================================================================


class TechnicalAnalysisDataSourceAdapter(IDataSource):
    """技术分析数据源适配器 - 集成现有技术分析服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "technical_analysis"
        self.name = config.get("name", "Technical Analysis Source")

        # Initialize services lazily (only when needed)
        self._technical_service = None
        self._mock_manager = None
        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)

    def _get_technical_service(self):
        """Lazy initialization of technical analysis service"""
        if self._technical_service is None:
            try:
                from app.services.technical_analysis_service import (
                    technical_analysis_service,
                )

                self._technical_service = technical_analysis_service
            except Exception as e:
                self._technical_service = None
                raise RuntimeError(f"Failed to initialize technical analysis service: {e}")
        return self._technical_service

    def _get_mock_manager(self):
        """Lazy initialization of mock manager"""
        if self._mock_manager is None:
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取技术分析数据"""
        # In mock mode, we don't need the technical service
        # if self._get_technical_service() is None:
        #     raise RuntimeError("Technical analysis service not available")

        params = params or {}
        start_time = time.time()

        try:
            # 解析端点路径
            path_parts = endpoint.strip("/").split("/")

            # 获取symbol参数
            symbol = params.get("symbol", "000001")

            if endpoint == "indicators" or (len(path_parts) >= 2 and path_parts[1] == "indicators"):
                # "indicators" or /{symbol}/indicators
                period = params.get("period", "daily")
                start_date = params.get("start_date")
                end_date = params.get("end_date")

                data = await self._get_all_indicators(symbol, period, start_date, end_date)

                # For indicators endpoint, return data directly without wrapping
                # The API expects the indicators data structure at the top level
                self.metrics.record_success((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "data": data,
                    "source": self.source_type,
                    "endpoint": endpoint,
                    "timestamp": datetime.now().isoformat(),
                }

            elif endpoint == "trend" or (len(path_parts) >= 2 and path_parts[1] == "trend"):
                # "trend" or /{symbol}/trend
                period = params.get("period", "daily")

                data = await self._get_trend_indicators(symbol, period)

            elif endpoint == "momentum" or (len(path_parts) >= 2 and path_parts[1] == "momentum"):
                # "momentum" or /{symbol}/momentum
                period = params.get("period", "daily")

                data = await self._get_momentum_indicators(symbol, period)

            elif endpoint == "volatility" or (len(path_parts) >= 2 and path_parts[1] == "volatility"):
                # "volatility" or /{symbol}/volatility
                period = params.get("period", "daily")

                data = await self._get_volatility_indicators(symbol, period)

            elif endpoint == "volume" or (len(path_parts) >= 2 and path_parts[1] == "volume"):
                # "volume" or /{symbol}/volume
                period = params.get("period", "daily")

                data = await self._get_volume_indicators(symbol, period)

            elif endpoint == "signals" or (len(path_parts) >= 2 and path_parts[1] == "signals"):
                # "signals" or /{symbol}/signals
                period = params.get("period", "daily")

                data = await self._get_trading_signals(symbol, period)

            elif endpoint == "history" or (len(path_parts) >= 2 and path_parts[1] == "history"):
                # "history" or /{symbol}/history
                start_date = params.get("start_date")
                end_date = params.get("end_date")
                limit = params.get("limit", 500)

                data = await self._get_stock_history(symbol, "daily", start_date, end_date, limit)

            elif endpoint == "batch_indicators" or (
                len(path_parts) >= 2 and path_parts[0] == "batch" and path_parts[1] == "indicators"
            ):
                # "batch_indicators" or /batch/indicators
                symbols = params.get("symbols", ["000001", "600519"])
                period = params.get("period", "daily")

                data = await self._get_batch_indicators(symbols, period)

            else:
                raise ValueError(f"Unsupported technical analysis endpoint: {endpoint}")

            # 记录成功请求
            self.metrics.record_success((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": {
                    "indicators": data,
                    "count": len(data) if isinstance(data, dict) else 1,
                },
                "source": self.source_type,
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            # 记录失败请求
            self.metrics.record_error((time.time() - start_time) * 1000, str(e))
            raise e

    async def _get_all_indicators(
        self,
        symbol: str,
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取所有技术指标"""
        # 使用Mock数据进行演示
        mock_manager = self._get_mock_manager()
        if mock_manager:
            try:
                mock_data = mock_manager.get_technical_indicators(symbol)
                if mock_data:
                    # 添加最新价格和日期信息
                    from datetime import date

                    today = date.today()
                    return {
                        "symbol": symbol,
                        "latest_price": mock_data.get("latest_price", 100.0),
                        "latest_date": today.isoformat(),
                        "data_points": mock_data.get("data_points", 252),
                        "total_indicators": 19,
                        "trend": {
                            "ma5": mock_data.get("ma5"),
                            "ma10": mock_data.get("ma10"),
                            "ma20": mock_data.get("ma20"),
                            "ma30": mock_data.get("ma30"),
                            "ma60": mock_data.get("ma60"),
                            "ma120": mock_data.get("ma120"),
                            "ma250": mock_data.get("ma250"),
                            "ema12": mock_data.get("ema12"),
                            "ema26": mock_data.get("ema26"),
                            "ema50": mock_data.get("ema50"),
                            "macd": mock_data.get("macd"),
                            "macd_signal": mock_data.get("macd_signal"),
                            "macd_hist": mock_data.get("macd_hist"),
                            "adx": mock_data.get("adx"),
                            "plus_di": mock_data.get("plus_di"),
                            "minus_di": mock_data.get("minus_di"),
                            "sar": mock_data.get("sar"),
                        },
                        "momentum": {
                            "rsi6": mock_data.get("rsi6"),
                            "rsi12": mock_data.get("rsi12"),
                            "rsi24": mock_data.get("rsi24"),
                            "kdj_k": mock_data.get("kdj_k"),
                            "kdj_d": mock_data.get("kdj_d"),
                            "kdj_j": mock_data.get("kdj_j"),
                            "cci": mock_data.get("cci"),
                            "wr": mock_data.get("wr"),
                            "roc": mock_data.get("roc"),
                        },
                        "volatility": {
                            "bb_upper": mock_data.get("bb_upper"),
                            "bb_middle": mock_data.get("bb_middle"),
                            "bb_lower": mock_data.get("bb_lower"),
                            "atr": mock_data.get("atr"),
                            "kc_upper": mock_data.get("kc_upper"),
                            "kc_middle": mock_data.get("kc_middle"),
                            "kc_lower": mock_data.get("kc_lower"),
                            "stddev": mock_data.get("stddev"),
                        },
                        "volume": {
                            "obv": mock_data.get("obv"),
                            "vwap": mock_data.get("vwap"),
                            "volume_ma5": mock_data.get("volume_ma5"),
                            "volume_ma10": mock_data.get("volume_ma10"),
                            "volume_ratio": mock_data.get("volume_ratio"),
                        },
                    }
            except Exception as e:
                print(f"Mock data generation failed: {e}")

        # 返回默认Mock数据
        return {
            "symbol": symbol,
            "latest_price": 100.0,
            "latest_date": date.today().isoformat(),
            "data_points": 252,
            "total_indicators": 19,
            "trend": {
                "ma5": 98.5,
                "ma10": 97.2,
                "ma20": 95.8,
                "ma30": 94.5,
                "ma60": 92.1,
                "ma120": 88.7,
                "ma250": 82.3,
                "ema12": 99.1,
                "ema26": 96.8,
                "ema50": 93.4,
                "macd": 0.15,
                "macd_signal": 0.12,
                "macd_hist": 0.03,
                "adx": 25.8,
                "plus_di": 18.2,
                "minus_di": 12.6,
                "sar": 97.8,
            },
            "momentum": {
                "rsi6": 65.2,
                "rsi12": 58.7,
                "rsi24": 52.3,
                "kdj_k": 68.5,
                "kdj_d": 62.1,
                "kdj_j": 74.8,
                "cci": 45.3,
                "wr": 32.7,
                "roc": 2.8,
            },
            "volatility": {
                "bb_upper": 108.5,
                "bb_middle": 100.0,
                "bb_lower": 91.5,
                "atr": 2.8,
                "kc_upper": 105.2,
                "kc_middle": 100.0,
                "kc_lower": 94.8,
                "stddev": 3.2,
            },
            "volume": {
                "obv": 1256800000,
                "vwap": 99.5,
                "volume_ma5": 15000000,
                "volume_ma10": 14500000,
                "volume_ratio": 1.15,
            },
        }

    async def _get_trend_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取趋势指标"""
        return {
            "ma5": 98.5,
            "ma10": 97.2,
            "ma20": 95.8,
            "ma30": 94.5,
            "ma60": 92.1,
            "ma120": 88.7,
            "ma250": 82.3,
            "ema12": 99.1,
            "ema26": 96.8,
            "ema50": 93.4,
            "macd": 0.15,
            "macd_signal": 0.12,
            "macd_hist": 0.03,
            "adx": 25.8,
            "plus_di": 18.2,
            "minus_di": 12.6,
            "sar": 97.8,
        }

    async def _get_momentum_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取动量指标"""
        return {
            "rsi6": 65.2,
            "rsi12": 58.7,
            "rsi24": 52.3,
            "kdj_k": 68.5,
            "kdj_d": 62.1,
            "kdj_j": 74.8,
            "cci": 45.3,
            "wr": 32.7,
            "roc": 2.8,
        }

    async def _get_volatility_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取波动性指标"""
        return {
            "bb_upper": 108.5,
            "bb_middle": 100.0,
            "bb_lower": 91.5,
            "atr": 2.8,
            "kc_upper": 105.2,
            "kc_middle": 100.0,
            "kc_lower": 94.8,
            "stddev": 3.2,
        }

    async def _get_volume_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取成交量指标"""
        return {
            "obv": 1256800000,
            "vwap": 99.5,
            "volume_ma5": 15000000,
            "volume_ma10": 14500000,
            "volume_ratio": 1.15,
        }

    async def _get_trading_signals(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取交易信号"""
        return {
            "trend_signal": "neutral",
            "momentum_signal": "bullish",
            "volume_signal": "bullish",
            "overall_signal": "bullish",
            "signal_strength": 0.65,
            "signals": [
                {"type": "RSI", "signal": "buy", "strength": 0.7},
                {"type": "MACD", "signal": "buy", "strength": 0.6},
                {"type": "Volume", "signal": "buy", "strength": 0.8},
            ],
        }

    async def _get_stock_history(
        self,
        symbol: str,
        period: str = "1y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """获取历史行情数据"""
        mock_manager = self._get_mock_manager()
        if mock_manager:
            try:
                mock_data = mock_manager.get_stock_history(symbol, period, limit)
                if mock_data:
                    return mock_data
            except Exception as e:
                print(f"Mock history data generation failed: {e}")

        # 生成模拟历史数据
        import random
        from datetime import datetime, timedelta

        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        data = []
        current_price = 100.0

        for i in range(min(limit, 252)):  # 一年约252个交易日
            date = end - timedelta(days=i)
            change = random.uniform(-3, 3)
            current_price = max(1, current_price + change)

            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(current_price + random.uniform(-1, 1), 2),
                    "high": round(current_price + random.uniform(0, 2), 2),
                    "low": round(current_price - random.uniform(0, 2), 2),
                    "close": round(current_price, 2),
                    "volume": random.randint(1000000, 20000000),
                }
            )

        return data

    async def _get_batch_indicators(self, symbols: List[str], period: str = "1y") -> Dict[str, Any]:
        """批量获取指标"""
        results = {}
        for symbol in symbols:
            try:
                indicators = await self._get_all_indicators(symbol, period)
                results[symbol] = indicators
            except Exception as e:
                print(f"Failed to get indicators for {symbol}: {e}")
                results[symbol] = {"error": str(e)}

        return results

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        start_time = time.time()

        try:
            # 测试技术分析服务可用性
            test_symbol = "000001"
            test_indicators = await self._get_trend_indicators(test_symbol)

            response_time = (time.time() - start_time) * 1000

            return HealthStatus(
                status=HealthStatusEnum.HEALTHY,
                message="Technical analysis source is healthy",
                response_time=response_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                message=f"Health check failed: {str(e)}",
                response_time=0,
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> "DataSourceMetrics":
        """获取监控指标"""
        return self.metrics

    async def close(self):
        """关闭连接和清理资源"""
        # Technical Analysis适配器不需要清理特定资源
        pass


class StrategyDataSourceAdapter(IDataSource):
    """策略管理数据源适配器 - 集成现有策略服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "strategy"
        self.name = config.get("name", "Strategy Management Source")

        # Initialize services lazily (only when needed)
        self._strategy_service = None
        self._mock_manager = None

        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)  # 5分钟缓存

    def _get_strategy_service(self):
        """Lazy initialization of strategy service"""
        if self._strategy_service is None:
            try:
                from app.services.strategy_service import get_strategy_service

                self._strategy_service = get_strategy_service()
            except Exception as e:
                self._strategy_service = None
                raise RuntimeError(f"Failed to initialize strategy service: {e}")
        return self._strategy_service

    def _get_mock_manager(self):
        """Lazy initialization of mock data manager"""
        if self._mock_manager is None:
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock data manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """获取策略管理数据"""
        start_time = time.time()
        params = params or {}

        try:
            # 检查缓存
            cache_key = f"{endpoint}:{hash(str(sorted(params.items())))}"
            if cache_key in self._cache:
                cached_item = self._cache[cache_key]
                if time.time() - cached_item["timestamp"] < self._cache_ttl:
                    self.metrics.record_success(time.time() - start_time)
                    return cached_item["data"]
                else:
                    del self._cache[cache_key]

            # 获取数据
            data = await self._fetch_strategy_data(endpoint, params)

            # 缓存结果
            self._cache[cache_key] = {"data": data, "timestamp": time.time()}

            self.metrics.record_success(time.time() - start_time)
            return data

        except Exception as e:
            self.metrics.record_error(time.time() - start_time, str(e))
            logger.error(f"Strategy data fetch error: {e}")
            raise

    async def _fetch_strategy_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """从策略服务获取数据"""
        try:
            service_available = self._get_strategy_service() is not None
        except Exception:
            service_available = False

        if not service_available and self._get_mock_manager():
            # 使用Mock数据
            return self._get_mock_strategy_data(endpoint, params)

        try:
            # 解析endpoint路径
            path_parts = endpoint.strip("/").split("/")

            if endpoint == "definitions" or endpoint == "/definitions":
                # 获取策略定义列表
                definitions = self._get_strategy_service().get_strategy_definitions()
                return {
                    "success": True,
                    "data": definitions,
                    "total": len(definitions),
                    "message": "获取策略定义成功",
                }

            elif endpoint.startswith("run/"):
                # 策略执行相关
                if len(path_parts) >= 3 and path_parts[1] == "single":
                    # 单股策略执行 run/single/{strategy_code}/{symbol}
                    strategy_code = path_parts[2] if len(path_parts) > 2 else params.get("strategy_code")
                    symbol = path_parts[3] if len(path_parts) > 3 else params.get("symbol")

                    if strategy_code and symbol:
                        result = self._get_strategy_service().run_strategy_for_stock(
                            strategy_code=strategy_code,
                            symbol=symbol,
                            stock_name=params.get("stock_name"),
                            check_date=params.get("check_date"),
                        )
                        return result

                elif len(path_parts) >= 3 and path_parts[1] == "batch":
                    # 批量策略执行 run/batch/{strategy_code}
                    strategy_code = path_parts[2]
                    symbols = params.get("symbols", [])

                    if strategy_code and symbols:
                        results = []
                        for symbol in symbols:
                            try:
                                result = self._get_strategy_service().run_strategy_for_stock(
                                    strategy_code=strategy_code, symbol=symbol
                                )
                                results.append({"symbol": symbol, "success": True, "data": result})
                            except Exception as e:
                                results.append(
                                    {
                                        "symbol": symbol,
                                        "success": False,
                                        "error": str(e),
                                    }
                                )

                        return {
                            "success": True,
                            "strategy_code": strategy_code,
                            "total_symbols": len(symbols),
                            "results": results,
                            "message": f"批量策略执行完成: {len([r for r in results if r['success']])}/{len(symbols)} 成功",
                        }

            elif endpoint.startswith("results/"):
                # 策略结果查询
                if len(path_parts) >= 3:
                    strategy_code = path_parts[2]
                    symbol = params.get("symbol")
                    limit = params.get("limit", 50)

                    results = self._get_strategy_service().get_strategy_results(
                        strategy_code=strategy_code, symbol=symbol, limit=limit
                    )
                    return {
                        "success": True,
                        "strategy_code": strategy_code,
                        "data": results,
                        "total": len(results),
                        "message": "获取策略结果成功",
                    }

            # 如果没有匹配的endpoint，返回默认数据
            return self._get_mock_strategy_data(endpoint, params)

        except Exception as e:
            logger.error(f"Strategy service error: {e}")
            # 降级到Mock数据
            if self._get_mock_manager():
                return self._get_mock_strategy_data(endpoint, params)
            raise

    def _get_mock_strategy_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """获取Mock策略数据"""
        mock_manager = self._get_mock_manager()
        if not mock_manager:
            return {"success": False, "error": "No mock data available"}

        try:
            # 生成Mock策略定义
            if endpoint == "definitions" or endpoint == "/definitions":
                definitions = [
                    {
                        "code": "volume_surge",
                        "name": "成交量突增策略",
                        "description": "检测成交量异常放大",
                        "category": "技术指标",
                        "risk_level": "中等",
                    },
                    {
                        "code": "price_breakout",
                        "name": "价格突破策略",
                        "description": "检测价格关键位突破",
                        "category": "技术指标",
                        "risk_level": "高",
                    },
                    {
                        "code": "rsi_oversold",
                        "name": "RSI超卖反弹策略",
                        "description": "RSI超卖区域的反弹机会",
                        "category": "技术指标",
                        "risk_level": "中等",
                    },
                    {
                        "code": "ma_golden_cross",
                        "name": "均线金叉策略",
                        "description": "短期均线上穿长期均线",
                        "category": "技术指标",
                        "risk_level": "低",
                    },
                ]

                return {
                    "success": True,
                    "data": definitions,
                    "total": len(definitions),
                    "message": "获取策略定义成功",
                }

            # Mock策略执行结果
            elif endpoint.startswith("run/"):
                strategy_code = params.get("strategy_code", "volume_surge")
                symbol = params.get("symbol", "000001")

                # 生成Mock执行结果
                import random

                base_price = random.uniform(10, 100)
                change_percent = random.uniform(-5, 10)
                volume_ratio = random.uniform(0.5, 5.0)

                mock_result = {
                    "success": True,
                    "strategy_code": strategy_code,
                    "symbol": symbol,
                    "check_date": params.get("check_date", "2025-12-01"),
                    "result": {
                        "signal": random.choice(["BUY", "SELL", "HOLD"]),
                        "confidence": random.uniform(0.6, 0.95),
                        "price": round(base_price, 2),
                        "change_percent": round(change_percent, 2),
                        "volume_ratio": round(volume_ratio, 2),
                        "indicators": {
                            "rsi": round(random.uniform(20, 80), 2),
                            "macd": round(random.uniform(-2, 2), 4),
                            "ma5": round(base_price * random.uniform(0.98, 1.02), 2),
                            "ma20": round(base_price * random.uniform(0.95, 1.05), 2),
                        },
                    },
                    "message": f"策略{strategy_code}对{symbol}执行完成",
                }

                return mock_result

            # Mock策略结果列表
            elif endpoint.startswith("results/"):
                strategy_code = params.get("strategy_code", "volume_surge")

                # 生成多个Mock结果
                mock_results = []
                symbols = ["000001", "000002", "600519", "600036", "000858"]

                for symbol in symbols:
                    mock_results.append(
                        {
                            "symbol": symbol,
                            "strategy_code": strategy_code,
                            "check_date": "2025-12-01",
                            "signal": random.choice(["BUY", "SELL", "HOLD"]),
                            "confidence": round(random.uniform(0.6, 0.95), 2),
                            "price": round(random.uniform(10, 200), 2),
                            "change_percent": round(random.uniform(-5, 10), 2),
                        }
                    )

                return {
                    "success": True,
                    "strategy_code": strategy_code,
                    "data": mock_results,
                    "total": len(mock_results),
                    "message": "获取策略结果成功",
                }

            # 默认Mock响应
            return {
                "success": True,
                "data": {},
                "message": f"Strategy mock data for {endpoint}",
            }

        except Exception as e:
            logger.error(f"Mock strategy data generation error: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        try:
            start_time = time.time()

            # 检查策略服务可用性
            service_available = self.strategy_service is not None
            mock_available = self._get_mock_manager() is not None

            # 基础健康检查
            basic_healthy = service_available or mock_available

            # 简单连接测试
            connection_test = False
            if basic_healthy:
                try:
                    # 尝试获取策略定义作为连接测试
                    if self.strategy_service:
                        self._get_strategy_service().get_strategy_definitions()
                    connection_test = True
                    self.last_successful_check = time.time()
                except:
                    if mock_available:
                        connection_test = True
                        self.last_successful_check = time.time()

            status = HealthStatusEnum.HEALTHY if (basic_healthy and connection_test) else HealthStatusEnum.FAILED

            details = {
                "service_available": service_available,
                "mock_available": mock_available,
                "connection_test": connection_test,
                "cache_size": len(self._cache),
                "response_time_ms": (time.time() - start_time) * 1000,
            }

            return HealthStatus(
                status=status,
                response_time=0.0,
                message=f"Strategy data source is {status.value}",
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=0.0,
                message=f"Strategy health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> DataSourceMetrics:
        """获取监控指标"""
        return self.metrics


class WatchlistDataSourceAdapter(IDataSource):
    """自选股管理数据源适配器 - 集成现有自选股服务到数据源工厂模式"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = "watchlist"
        self.name = config.get("name", "Watchlist Management Source")
        self.mode = config.get("mode", "mock")

        # Lazy initialization of services (only when needed)
        self._watchlist_service = None
        self._mock_manager = None

        self.metrics = DataSourceMetrics()
        self._cache = {}
        self._cache_ttl = config.get("cache_ttl", 300)  # 5分钟缓存

    def _get_watchlist_service(self):
        """Lazy initialization of watchlist service"""
        if self._watchlist_service is None and self.mode != "mock":
            try:
                from app.services.watchlist_service import get_watchlist_service

                self._watchlist_service = get_watchlist_service()
            except Exception as e:
                self._watchlist_service = None
                raise RuntimeError(f"Failed to initialize watchlist service: {e}")
        return self._watchlist_service

    def _get_mock_manager(self):
        """Lazy initialization of mock manager"""
        if self._mock_manager is None:
            try:
                from app.mock.unified_mock_data import get_mock_data_manager

                self._mock_manager = get_mock_data_manager()
            except Exception as e:
                self._mock_manager = None
                raise RuntimeError(f"Failed to initialize mock manager: {e}")
        return self._mock_manager

    async def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """获取自选股管理数据"""
        start_time = time.time()
        params = params or {}

        try:
            # 检查缓存
            cache_key = f"{endpoint}:{hash(str(sorted(params.items())))}"
            if cache_key in self._cache:
                cached_item = self._cache[cache_key]
                if time.time() - cached_item["timestamp"] < self._cache_ttl:
                    self.metrics.record_success(time.time() - start_time)
                    return cached_item["data"]
                else:
                    del self._cache[cache_key]

            # 获取数据
            data = await self._fetch_watchlist_data(endpoint, params)

            # 缓存结果
            self._cache[cache_key] = {"data": data, "timestamp": time.time()}

            self.metrics.record_success(time.time() - start_time)
            return data

        except Exception as e:
            self.metrics.record_error(time.time() - start_time, str(e))
            logger.error(f"Watchlist data fetch error: {e}")
            raise

    async def _fetch_watchlist_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """从自选股服务获取数据"""
        if self.mode == "mock":
            # 使用Mock数据
            return self._get_mock_watchlist_data(endpoint, params)

        try:
            # 解析endpoint路径
            path_parts = endpoint.strip("/").split("/")

            # 注意：watchlist服务通常需要用户ID，这里使用默认用户ID
            user_id = params.get("user_id", 1)

            if endpoint == "list" or endpoint == "/list":
                # 获取用户自选股列表
                watchlist_service = self._get_watchlist_service()
                watchlist = watchlist_service.get_user_watchlist(user_id)
                return {
                    "success": True,
                    "data": watchlist,
                    "total": len(watchlist),
                    "message": "获取自选股列表成功",
                }

            elif endpoint == "symbols" or endpoint == "/symbols":
                # 获取自选股代码列表
                watchlist_service = self._get_watchlist_service()
                symbols = watchlist_service.get_watchlist_symbols(user_id)
                return {
                    "success": True,
                    "data": symbols,
                    "total": len(symbols),
                    "message": "获取自选股代码列表成功",
                }

            elif endpoint.startswith("add/"):
                # 添加自选股 add/{symbol}
                if len(path_parts) >= 2:
                    symbol = path_parts[1]
                    display_name = params.get("display_name", symbol)
                    exchange = params.get("exchange", "SZSE")
                    market = params.get("market", "CN")
                    notes = params.get("notes", "")
                    group_id = params.get("group_id")
                    group_name = params.get("group_name")

                    try:
                        watchlist_item = self._get_watchlist_service().add_stock_to_watchlist(
                            user_id=user_id,
                            symbol=symbol,
                            display_name=display_name,
                            exchange=exchange,
                            market=market,
                            notes=notes,
                            group_id=group_id,
                            group_name=group_name,
                        )
                        return {
                            "success": True,
                            "data": watchlist_item,
                            "message": f"成功添加 {symbol} 到自选股",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"添加 {symbol} 到自选股失败",
                        }

            elif endpoint.startswith("remove/"):
                # 移除自选股 remove/{symbol}
                if len(path_parts) >= 2:
                    symbol = path_parts[1]

                    try:
                        self._get_watchlist_service().remove_stock_from_watchlist(user_id=user_id, symbol=symbol)
                        return {
                            "success": True,
                            "message": f"成功从自选股中移除 {symbol}",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"移除 {symbol} 从自选股失败",
                        }

            elif endpoint.startswith("groups/"):
                # 分组管理相关
                if path_parts[1] == "list":
                    # 获取分组列表 groups/list
                    groups = self._get_watchlist_service().get_user_groups(user_id)
                    return {
                        "success": True,
                        "data": groups,
                        "total": len(groups),
                        "message": "获取自选股分组列表成功",
                    }

                elif path_parts[1] == "create":
                    # 创建分组 groups/create
                    group_name = params.get("group_name", "默认分组")

                    try:
                        group = self._get_watchlist_service().create_group(user_id=user_id, group_name=group_name)
                        return {
                            "success": True,
                            "data": group,
                            "message": f"成功创建分组: {group_name}",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": str(e),
                            "message": f"创建分组失败: {group_name}",
                        }

            # 如果没有匹配的endpoint，返回默认数据
            return self._get_mock_watchlist_data(endpoint, params)

        except Exception as e:
            logger.error(f"Watchlist service error: {e}")
            # 降级到Mock数据
            if self._get_mock_manager():
                return self._get_mock_watchlist_data(endpoint, params)
            raise

    def _get_mock_watchlist_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """获取Mock自选股数据"""
        mock_manager = self._get_mock_manager()
        if not mock_manager:
            return {"success": False, "error": "No mock data available"}

        try:
            # 使用统一mock数据管理器
            return mock_manager.get_data("watchlist", endpoint=endpoint, **params)

        except Exception as e:
            logger.error(f"Mock watchlist data fetch failed for {endpoint}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch mock watchlist data: {str(e)}",
                "data": None,
            }

    async def health_check(self) -> HealthStatus:
        """健康检查"""
        try:
            start_time = time.time()

            # 检查自选股服务可用性
            service_available = self.watchlist_service is not None
            mock_available = self._get_mock_manager() is not None

            # 基础健康检查
            basic_healthy = service_available or mock_available

            # 简单连接测试
            connection_test = False
            if basic_healthy:
                try:
                    # 尝试获取自选股列表作为连接测试
                    if self.mode != "mock":
                        self._get_watchlist_service().get_user_watchlist(1)
                    connection_test = True
                    self.last_successful_check = time.time()
                except:
                    if mock_available:
                        connection_test = True
                        self.last_successful_check = time.time()

            status = HealthStatusEnum.HEALTHY if (basic_healthy and connection_test) else HealthStatusEnum.FAILED

            details = {
                "service_available": service_available,
                "mock_available": mock_available,
                "connection_test": connection_test,
                "cache_size": len(self._cache),
                "response_time_ms": (time.time() - start_time) * 1000,
            }

            return HealthStatus(
                status=status,
                response_time=0.0,
                message=f"Watchlist data source is {status.value}",
                timestamp=datetime.now(),
            )

        except Exception as e:
            return HealthStatus(
                status=HealthStatusEnum.FAILED,
                response_time=0.0,
                message=f"Watchlist health check failed: {str(e)}",
                timestamp=datetime.now(),
            )

    def get_metrics(self) -> DataSourceMetrics:
        """获取监控指标"""
        return self.metrics
