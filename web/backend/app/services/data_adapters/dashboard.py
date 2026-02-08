"""
仪表盘数据源适配器
"""
import time
import logging
import random
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.data_quality_monitor import get_data_quality_monitor
from app.services.data_source_interface import (
    HealthStatus,
    HealthStatusEnum,
    IDataSource,
)
from .base import DataSourceMetrics

logger = logging.getLogger(__name__)

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
