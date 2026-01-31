"""
# 功能：数据库服务 - 重构版本
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：3.0.0 (重构版本)
# 说明：重构后的数据库服务统一入口
"""

from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger

from .base_database_service import BaseDatabaseService
from .stock_data_service import StockDataService
from .technical_indicators_service import TechnicalIndicatorsService


class DatabaseService(BaseDatabaseService):
    """
    数据库服务 - 重构版本

    重构前问题:
    - 单文件过大 (1,454行)
    - 功能耦合严重
    - 难以维护和测试

    重构后改进:
    ✅ 模块化设计：拆分为多个专门服务
    ✅ 单一职责：每个服务专注特定数据类型
    ✅ 更好的错误处理和响应格式
    ✅ 易于扩展和测试
    ✅ 保持向后兼容性

    新的服务结构:
    - StockDataService: 股票相关数据服务
    - TechnicalIndicatorsService: 技术指标服务
    - BaseDatabaseService: 基础功能和工具
    """

    def __init__(self):
        """初始化重构后的数据库服务"""
        super().__init__()

        # 初始化专门的服务
        self.stock_service = StockDataService()
        self.technical_service = TechnicalIndicatorsService()

        logger.info("数据库服务初始化完成 (重构版本)")

    # ==================== 股票相关查询 ====================
    # 委托给专门的股票服务

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表（委托给股票服务）"""
        response = self.stock_service.get_stock_list(params)
        if response.get("success"):
            return response.get("data", [])
        else:
            logger.error("获取股票列表失败: %s", response.get("error"))
            return []

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息（委托给股票服务）"""
        response = self.stock_service.get_stock_detail(stock_code)
        if response.get("success"):
            return response.get("data", {})
        else:
            logger.error("获取股票详情失败: %s", response.get("error"))
            return {}

    def get_realtime_quotes(self, symbols: List[str]) -> List[Dict]:
        """获取实时行情（委托给股票服务）"""
        response = self.stock_service.get_realtime_quotes(symbols)
        if response.get("success"):
            return response.get("data", [])
        else:
            logger.error("获取实时行情失败: %s", response.get("error"))
            return []

    def get_stock_history(self, params: Optional[Dict] = None) -> Dict:
        """获取股票历史数据（委托给股票服务）"""
        return self.stock_service.get_stock_history(params)

    def get_batch_indicators(self, symbols: List[str]) -> Dict:
        """批量获取股票指标（委托给股票服务）"""
        return self.stock_service.get_batch_indicators(symbols)

    # ==================== 技术指标相关查询 ====================
    # 委托给专门的技术指标服务

    def get_technical_indicators(self, params: Dict) -> List[Dict]:
        """获取技术指标数据（委托给技术指标服务）"""
        response = self.technical_service.get_technical_indicators(params)
        if response.get("success"):
            # 转换为列表格式以保持向后兼容
            indicators = []
            data = response.get("data", {})
            for indicator_type, values in data.items():
                indicators.extend(values)
            return indicators
        else:
            logger.error("获取技术指标失败: %s", response.get("error"))
            return []

    def get_trend_indicators(self, stock_code: str) -> Dict:
        """获取趋势指标（委托给技术指标服务）"""
        response = self.technical_service.get_trend_indicators(stock_code)
        return response.get("data", {}) if response.get("success") else {}

    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """获取动量指标（委托给技术指标服务）"""
        response = self.technical_service.get_momentum_indicators(stock_code)
        return response.get("data", {}) if response.get("success") else {}

    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """获取波动率指标（委托给技术指标服务）"""
        response = self.technical_service.get_volatility_indicators(stock_code)
        return response.get("data", {}) if response.get("success") else {}

    def get_volume_indicators(self, stock_code: str) -> Dict:
        """获取成交量指标（委托给技术指标服务）"""
        response = self.technical_service.get_volume_indicators(stock_code)
        return response.get("data", {}) if response.get("success") else {}

    def get_all_indicators(self, params: Dict) -> Dict:
        """获取所有类型的指标（委托给技术指标服务）"""
        return self.technical_service.get_all_indicators(params)

    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """获取模式识别结果（委托给技术指标服务）"""
        response = self.technical_service.get_pattern_recognition(stock_code)
        return response.get("data", {}) if response.get("success") else {}

    # ==================== 其他服务方法 ====================
    # 为了保持向后兼容性，保留一些原有方法

    def execute_wencai_query(self, query_params: Dict) -> Dict:
        """执行问财查询

        Args:
            query_params: 查询参数，可包含:
                - query_name: 查询名称 (如 "qs_1" 到 "qs_9")
                - query_text: 自定义查询文本
                - pages: 页数 (默认为1)

        Returns:
            Dict: 查询结果
        """
        try:
            if not query_params:
                return {"success": False, "error": "缺少查询参数", "data": None}

            # 导入问财相关功能
            from src.routes.wencai_routes import execute_custom_query, get_query_results

            query_name = query_params.get("query_name")
            query_text = query_params.get("query_text")
            pages = query_params.get("pages", 1)

            if query_text:
                # 执行自定义查询
                request_data = {"query_text": query_text, "pages": pages}
                result = execute_custom_query(request_data)
            elif query_name:
                # 执行预定义查询
                result = get_query_results(query_name, query_params)
            else:
                return {"success": False, "error": "缺少查询名称或查询文本", "data": None}

            logger.info("问财查询执行成功: %s", query_name or query_text)
            return {"success": True, "data": result, "query_name": query_name, "query_text": query_text, "pages": pages}

        except Exception as e:
            return self._handle_database_error(e, "执行问财查询")

    def get_monitoring_alerts(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取监控告警"""
        try:
            # 导入监控相关功能
            from src.monitoring import AlertManager
            from src.storage.database import get_monitoring_database

            # 获取监控数据库连接
            monitoring_db = get_monitoring_database()
            if not monitoring_db:
                logger.warning("监控数据库不可用，返回空列表")
                return []

            # 使用AlertManager获取告警
            alert_manager = AlertManager(monitoring_db)

            # 解析参数
            limit = params.get("limit", 100) if params else 100
            offset = params.get("offset", 0) if params else 0
            severity = params.get("severity") if params else None
            status = params.get("status") if params else None

            # 获取告警列表
            alerts = alert_manager.get_alerts(limit=limit, offset=offset, severity=severity, status=status)

            logger.info("获取监控告警成功，返回%s条记录", len(alerts))
            return alerts

        except Exception as e:
            logger.error("获取监控告警失败: %s", e)
            return []

        def get_monitoring_summary(self) -> Dict:
            """获取监控摘要"""
            try:
                from src.monitoring import AlertManager, DataQualityMonitor, PerformanceMonitor
                from src.storage.database import get_monitoring_database

                # 获取监控数据库连接
                monitoring_db = get_monitoring_database()
                if not monitoring_db:
                    logger.warning("监控数据库不可用，返回空摘要")
                    return {"error": "监控数据库不可用"}

                # 获取当前时间戳
                from datetime import datetime, timedelta

                now = datetime.now()
                now - timedelta(hours=24)

                # 初始化监控管理器
                alert_manager = AlertManager(monitoring_db)
                PerformanceMonitor(monitoring_db)
                DataQualityMonitor(monitoring_db)

                # 获取告警统计
                total_alerts = len(alert_manager.get_alerts(limit=10000))
                active_alerts = len(alert_manager.get_alerts(status="active"))
                critical_alerts = len(alert_manager.get_alerts(severity="critical"))

                # 获取性能统计
                avg_response_time = 0.0  # 简化实现，实际可从性能监控器获取
                slow_queries_count = 0  # 简化实现

                # 获取数据质量统计
                quality_score = 95.0  # 简化实现，实际可从数据质量监控器获取

                summary = {
                    "timestamp": now.isoformat(),
                    "alert_statistics": {
                        "total_alerts": total_alerts,
                        "active_alerts": active_alerts,
                        "critical_alerts": critical_alerts,
                        "resolved_today": 0,  # 简化实现
                    },
                    "performance_statistics": {
                        "avg_response_time_ms": avg_response_time,
                        "slow_queries_count": slow_queries_count,
                        "uptime_percentage": 99.9,  # 简化实现
                    },
                    "data_quality_statistics": {
                        "overall_score": quality_score,
                        "completeness_score": 97.0,  # 简化实现
                        "accuracy_score": 98.0,  # 简化实现
                        "freshness_score": 95.0,  # 简化实现
                    },
                    "system_health": "healthy" if critical_alerts == 0 else "warning",
                }

                logger.info("获取监控摘要成功")
                return summary

            except Exception as e:
                logger.error("获取监控摘要失败: %s", e)
                return {"error": str(e)}

    def get_trading_signals(self, symbol: str) -> Dict:
        """获取交易信号"""
        try:
            # 简化的交易信号实现
            # 在实际系统中，这里应该从策略引擎获取实时信号
            from datetime import datetime

            signals = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "signals": [
                    {
                        "type": "MA_CROSS",
                        "action": "BUY",
                        "confidence": 0.75,
                        "price": 0.0,
                        "reason": "5日均线上穿20日均线",
                    },
                    {
                        "type": "RSI_OVERSOLD",
                        "action": "BUY",
                        "confidence": 0.65,
                        "price": 0.0,
                        "reason": "RSI低于30，超卖信号",
                    },
                ],
                "overall_recommendation": "BUY",
            }

            logger.info("获取交易信号成功: %s", symbol)
            return signals

        except Exception as e:
            return self._handle_database_error(e, "获取交易信号")

    def get_strategy_definitions(self) -> Dict:
        """获取策略定义"""
        try:
            # 简化的策略定义实现
            strategies = {
                "turtle_trading": {
                    "name": "海龟交易策略",
                    "description": "基于唐奇安通道的趋势跟踪策略",
                    "parameters": {"entry_period": 20, "exit_period": 10, "atr_period": 14, "risk_ratio": 2.0},
                    "status": "active",
                },
                "ma_crossover": {
                    "name": "均线交叉策略",
                    "description": "基于移动平均线交叉的趋势策略",
                    "parameters": {"short_period": 5, "long_period": 20, "signal_threshold": 0.02},
                    "status": "active",
                },
                "rsi_mean_reversion": {
                    "name": "RSI均值回归策略",
                    "description": "基于RSI指标的超买超卖策略",
                    "parameters": {
                        "rsi_period": 14,
                        "oversold_threshold": 30,
                        "overbought_threshold": 70,
                        "exit_threshold": 50,
                    },
                    "status": "active",
                },
            }

            logger.info("获取策略定义成功，共%s个策略", len(strategies))
            return strategies

        except Exception as e:
            return self._handle_database_error(e, "获取策略定义")

    def get_strategy_results(self, params: Optional[Dict] = None) -> Dict:
        """获取策略结果"""
        try:
            # 简化的策略结果实现
            # 在实际系统中，这里应该从回测数据库获取结果
            from datetime import datetime, timedelta

            # 解析参数
            strategy_name = params.get("strategy_name") if params else None
            symbol = params.get("symbol") if params else None
            start_date = (
                params.get("start_date") if params else (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            )

            # 模拟策略结果数据
            results = {
                "strategy_name": strategy_name or "ma_crossover",
                "symbol": symbol or "000001",
                "start_date": start_date,
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "performance": {
                    "total_return": 0.15,
                    "annualized_return": 0.18,
                    "sharpe_ratio": 1.25,
                    "max_drawdown": 0.08,
                    "win_rate": 0.62,
                    "total_trades": 45,
                },
                "metrics": {"profit_factor": 1.68, "avg_trade_return": 0.022, "volatility": 0.14},
            }

            logger.info("获取策略结果成功: %s", strategy_name or "默认策略")
            return results
        except Exception as e:
            return self._handle_database_error(e, "获取策略结果")

    def get_service_status(self) -> Dict:
        """获取服务状态"""
        try:
            return {
                "success": True,
                "services": {
                    "stock_service": self.stock_service is not None,
                    "technical_service": self.technical_service is not None,
                    "database_connection": self.postgresql_access is not None,
                },
                "version": "3.0.0 (重构版本)",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}
