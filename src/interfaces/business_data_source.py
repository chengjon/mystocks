"""
业务逻辑数据源抽象接口

本模块定义业务逻辑数据源的统一接口，用于处理复杂业务场景。
业务逻辑层通常需要混合时序数据和关系数据，执行复杂的计算和聚合操作。

适用场景: 仪表盘汇总、策略回测、风险分析、交易归因等复合业务

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import date


class IBusinessDataSource(ABC):
    """
    业务逻辑数据源抽象接口

    此接口封装复杂业务逻辑，内部协调时序数据源和关系数据源。
    业务层负责:
    1. 数据聚合和计算
    2. 多数据源协调
    3. 业务规则执行
    4. 性能优化（缓存、并行）

    实现类:
    - MockBusinessDataSource: Mock数据实现（开发测试）
    - BusinessDataSourceImpl: 真实业务实现（生产）
    """

    # ==================== 仪表盘相关 ====================

    @abstractmethod
    def get_dashboard_summary(self, user_id: int, trade_date: Optional[date] = None) -> Dict[str, Any]:
        """
        获取仪表盘汇总数据

        Args:
            user_id: 用户ID
            trade_date: 交易日期，None表示最新交易日

        Returns:
            Dict: 仪表盘汇总数据（混合时序+关系数据）

        示例返回:
            {
                "trade_date": "2025-11-21",
                "user_id": 1001,

                # 市场概览 (来自时序数据源)
                "market_overview": {
                    "total_stocks": 5234,
                    "up_stocks": 2845,
                    "down_stocks": 2103,
                    "limit_up": 45,
                    "limit_down": 12,
                    "indices": {
                        "sh000001": {"name": "上证指数", "close": 3250.5, "change": 1.2},
                        "sz399001": {"name": "深证成指", "close": 11234.8, "change": 0.8}
                    }
                },

                # 数据更新状态
                "data_status": {
                    "last_update": "2025-11-21 15:05:00",
                    "realtime_delay_seconds": 5,
                    "data_completeness": 98.5
                },

                # 市场热度 (板块+资金流)
                "market_hotspots": {
                    "top_industries": [
                        {"name": "计算机", "change": 3.2, "fund_inflow": 1250000000},
                        {"name": "电子", "change": 2.8, "fund_inflow": 980000000}
                    ],
                    "top_concepts": [
                        {"name": "人工智能", "change": 4.5, "stock_count": 123}
                    ]
                },

                # 资金流向排名
                "fund_flow_ranking": {
                    "top_inflow": [
                        {"symbol": "600000", "name": "浦发银行", "net_inflow": 125000000}
                    ],
                    "top_outflow": [
                        {"symbol": "600001", "name": "邯郸钢铁", "net_outflow": -85000000}
                    ]
                },

                # 用户自选股表现 (来自关系数据源)
                "watchlist_performance": {
                    "favorite_stocks": {
                        "total_count": 20,
                        "avg_change": 1.5,
                        "up_count": 15,
                        "down_count": 5
                    },
                    "strategy_stocks": {
                        "total_count": 35,
                        "avg_change": 2.3
                    }
                }
            }

        性能要求:
            - 总响应时间: < 1s
            - 使用并行查询优化
            - 缓存热点数据

        Raises:
            DataSourceException: 数据获取失败
        """
        pass

    @abstractmethod
    def get_sector_performance(
        self, sector_type: str, trade_date: Optional[date] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取板块表现

        Args:
            sector_type: 板块类型
                        - "industry": 行业板块
                        - "concept": 概念板块
            trade_date: 交易日期
            limit: 返回数量

        Returns:
            List[Dict]: 板块表现列表

        示例返回:
            [
                {
                    "code": "801010",
                    "name": "农林牧渔",
                    "stock_count": 123,
                    "avg_change": 2.3,
                    "up_count": 85,
                    "down_count": 38,
                    "total_amount": 12345678900.0,
                    "net_fund_inflow": 234567890.0,
                    "top_stocks": [
                        {"symbol": "000001", "name": "平安银行", "change": 5.2}
                    ]
                },
                ...
            ]

        性能要求: < 500ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    # ==================== 策略回测相关 ====================

    @abstractmethod
    def execute_backtest(
        self,
        strategy_id: int,
        user_id: int,
        start_date: date,
        end_date: date,
        initial_capital: float,
        universe: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        执行策略回测

        Args:
            strategy_id: 策略ID（从关系数据源获取配置）
            user_id: 用户ID（权限验证）
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
            universe: 股票池，None表示使用全市场

        Returns:
            Dict: 回测结果

        示例返回:
            {
                "backtest_id": "BT20251121001",
                "strategy_id": 1,
                "strategy_name": "动量策略001",
                "period": {
                    "start_date": "2024-01-01",
                    "end_date": "2025-11-21",
                    "trading_days": 245
                },

                # 收益指标
                "returns": {
                    "total_return": 0.235,  # 23.5%
                    "annual_return": 0.198,
                    "sharpe_ratio": 1.45,
                    "max_drawdown": -0.125,
                    "win_rate": 0.58
                },

                # 交易统计
                "trades": {
                    "total_trades": 128,
                    "profitable_trades": 74,
                    "losing_trades": 54,
                    "avg_profit": 0.032,
                    "avg_loss": -0.018
                },

                # 持仓统计
                "positions": {
                    "avg_holding_period": 8.5,  # 天
                    "max_positions": 10,
                    "turnover_rate": 1.5
                },

                # 净值曲线
                "equity_curve": [
                    {"date": "2024-01-01", "equity": 100000.0},
                    {"date": "2024-01-02", "equity": 101250.0},
                    ...
                ],

                # 详细交易记录
                "trade_records": [
                    {
                        "date": "2024-01-05",
                        "symbol": "600000",
                        "action": "buy",
                        "price": 10.5,
                        "quantity": 1000,
                        "amount": 10500.0
                    },
                    ...
                ],

                "created_at": "2025-11-21 15:00:00",
                "execution_time_seconds": 12.5
            }

        性能要求:
            - 1年数据(50股票): < 30s
            - 使用GPU加速可降至 < 10s

        Raises:
            DataSourceException: 回测执行失败
            PermissionError: 用户无权限
            ValueError: 参数无效
        """
        pass

    @abstractmethod
    def get_backtest_results(
        self,
        user_id: int,
        backtest_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        获取回测结果列表

        Args:
            user_id: 用户ID
            backtest_id: 回测ID，精确查询
            strategy_id: 策略ID，过滤查询
            limit: 返回数量

        Returns:
            List[Dict]: 回测结果列表（摘要版本）

        性能要求: < 200ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    # ==================== 风险管理相关 ====================

    @abstractmethod
    def calculate_risk_metrics(self, user_id: int, portfolio: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        计算风险指标

        Args:
            user_id: 用户ID
            portfolio: 投资组合 {"symbol": quantity}
                      None表示使用用户当前持仓

        Returns:
            Dict: 风险指标

        示例返回:
            {
                "user_id": 1001,
                "calculation_time": "2025-11-21 15:00:00",

                # VaR指标
                "var_metrics": {
                    "var_95": -12500.0,  # 95%置信度VaR
                    "var_99": -18750.0,
                    "cvar_95": -15230.0  # 条件VaR
                },

                # 波动率指标
                "volatility": {
                    "daily_volatility": 0.018,
                    "annual_volatility": 0.285,
                    "beta": 1.15,
                    "correlation_with_market": 0.72
                },

                # 集中度风险
                "concentration": {
                    "top1_weight": 0.25,
                    "top3_weight": 0.58,
                    "top5_weight": 0.75,
                    "herfindahl_index": 0.15
                },

                # 行业分布
                "industry_exposure": {
                    "金融": 0.35,
                    "科技": 0.28,
                    "消费": 0.20,
                    "其他": 0.17
                }
            }

        性能要求: < 800ms

        Raises:
            DataSourceException: 计算失败
        """
        pass

    @abstractmethod
    def check_risk_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """
        检查风险预警

        Args:
            user_id: 用户ID

        Returns:
            List[Dict]: 触发的预警列表

        示例返回:
            [
                {
                    "alert_id": 1,
                    "symbol": "600000",
                    "alert_type": "price",
                    "condition": ">=",
                    "threshold": 12.0,
                    "current_value": 12.5,
                    "triggered_at": "2025-11-21 14:35:00",
                    "message": "浦发银行价格达到12.5，触发预警（阈值12.0）"
                },
                ...
            ]

        性能要求: < 300ms

        Raises:
            DataSourceException: 检查失败
        """
        pass

    # ==================== 交易管理相关 ====================

    @abstractmethod
    def analyze_trading_signals(
        self,
        user_id: int,
        strategy_ids: Optional[List[int]] = None,
        trade_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        分析交易信号

        Args:
            user_id: 用户ID
            strategy_ids: 策略ID列表，None表示所有启用的策略
            trade_date: 交易日期，None表示最新交易日

        Returns:
            List[Dict]: 交易信号列表

        示例返回:
            [
                {
                    "signal_id": "SIG20251121001",
                    "strategy_id": 1,
                    "strategy_name": "动量策略001",
                    "symbol": "600000",
                    "name": "浦发银行",
                    "action": "buy",  # buy/sell/hold
                    "confidence": 0.85,
                    "price": 10.5,
                    "recommended_quantity": 1000,
                    "reason": "20日动量突破，成交量放大",
                    "generated_at": "2025-11-21 15:00:00"
                },
                ...
            ]

        性能要求: < 500ms

        Raises:
            DataSourceException: 分析失败
        """
        pass

    @abstractmethod
    def get_portfolio_analysis(self, user_id: int, include_history: bool = False) -> Dict[str, Any]:
        """
        获取持仓分析

        Args:
            user_id: 用户ID
            include_history: 是否包含历史持仓

        Returns:
            Dict: 持仓分析

        示例返回:
            {
                "user_id": 1001,
                "analysis_time": "2025-11-21 15:00:00",

                # 当前持仓
                "current_positions": [
                    {
                        "symbol": "600000",
                        "name": "浦发银行",
                        "quantity": 1000,
                        "cost_price": 10.0,
                        "current_price": 10.5,
                        "market_value": 10500.0,
                        "profit_loss": 500.0,
                        "profit_loss_percent": 5.0,
                        "weight": 0.15
                    },
                    ...
                ],

                # 持仓汇总
                "summary": {
                    "total_market_value": 70000.0,
                    "total_cost": 65000.0,
                    "total_profit_loss": 5000.0,
                    "total_return": 0.077,
                    "cash": 30000.0,
                    "total_assets": 100000.0
                },

                # 收益曲线（如果include_history=True）
                "equity_history": [
                    {"date": "2025-10-01", "equity": 95000.0},
                    {"date": "2025-11-21", "equity": 100000.0}
                ]
            }

        性能要求:
            - 不含历史: < 200ms
            - 含历史: < 500ms

        Raises:
            DataSourceException: 查询失败
        """
        pass

    @abstractmethod
    def perform_attribution_analysis(self, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        执行归因分析

        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 归因分析结果

        示例返回:
            {
                "period": {
                    "start_date": "2025-01-01",
                    "end_date": "2025-11-21",
                    "trading_days": 230
                },

                # 收益归因
                "return_attribution": {
                    "total_return": 0.077,
                    "market_return": 0.045,
                    "alpha": 0.032,
                    "attribution_breakdown": {
                        "sector_selection": 0.015,
                        "stock_selection": 0.020,
                        "timing": -0.003
                    }
                },

                # 行业贡献
                "sector_contribution": {
                    "金融": 0.025,
                    "科技": 0.035,
                    "消费": 0.012,
                    "其他": 0.005
                },

                # 个股贡献
                "top_contributors": [
                    {"symbol": "600000", "contribution": 0.015},
                    {"symbol": "000001", "contribution": 0.012}
                ],
                "top_detractors": [
                    {"symbol": "600001", "contribution": -0.008}
                ]
            }

        性能要求: < 1s

        Raises:
            DataSourceException: 分析失败
        """
        pass

    # ==================== 数据分析相关 ====================

    @abstractmethod
    def execute_stock_screener(
        self,
        user_id: int,
        criteria: Dict[str, Any],
        sort_by: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        执行股票筛选

        Args:
            user_id: 用户ID
            criteria: 筛选条件
                     {
                         "price_range": [10.0, 50.0],
                         "change_range": [0, 10],
                         "volume_min": 1000000,
                         "industry": ["银行", "保险"],
                         "technical_indicators": {
                             "rsi": {"min": 30, "max": 70},
                             "ma5_above_ma10": True
                         }
                     }
            sort_by: 排序字段 (change_percent/volume/amount等)
            limit: 返回数量

        Returns:
            List[Dict]: 筛选结果

        示例返回:
            [
                {
                    "symbol": "600000",
                    "name": "浦发银行",
                    "price": 10.5,
                    "change_percent": 2.94,
                    "volume": 125000000,
                    "industry": "银行",
                    "technical_scores": {
                        "rsi": 55.2,
                        "macd": "golden_cross"
                    }
                },
                ...
            ]

        性能要求: < 1.5s

        Raises:
            DataSourceException: 筛选失败
            ValueError: 筛选条件无效
        """
        pass

    # ==================== 健康检查 ====================

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        业务数据源健康检查

        Returns:
            Dict: 健康状态

        示例返回:
            {
                "status": "healthy",
                "data_source_type": "business",
                "dependencies": {
                    "timeseries_source": {"status": "healthy", "response_time_ms": 45},
                    "relational_source": {"status": "healthy", "response_time_ms": 25}
                },
                "cache_status": {
                    "enabled": True,
                    "hit_rate": 0.75,
                    "size_mb": 128
                },
                "last_calculation": "2025-11-21 14:59:55"
            }

        Raises:
            DataSourceException: 健康检查失败
        """
        pass
