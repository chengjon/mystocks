"""Mock 数据子模块"""

import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ._watchlist_data import get_watchlist_mock_data


logger = logging.getLogger(__name__)


class MockDataCoreMixin:
    """Mock 数据核心：初始化、路由、数据生成"""


class UnifiedMockDataManager:
    """统一Mock数据管理器"""

    def __init__(self, use_mock_data: bool = None):
        """初始化Mock数据管理器

        Args:
            use_mock_data: 是否使用Mock数据，如果为None则从环境变量读取

        """
        # 从环境变量获取数据源配置
        self.use_mock_data = use_mock_data or os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        # Mock数据目录
        self.mock_data_dir = Path(__file__).parent

        # 数据缓存
        self._data_cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 300  # 5分钟缓存

        logger.info("初始化Mock数据管理器，使用Mock数据: {self.use_mock_data}")

    def get_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取统一数据接口

        Args:
            data_type: 数据类型 (dashboard, stocks, technical, wencai, strategy, monitoring)
            **kwargs: 额外的查询参数

        Returns:
            数据响应

        """
        cache_key = f"{data_type}:{kwargs!s}"

        # 检查缓存
        if self._is_cache_valid(cache_key):
            logger.debug("从缓存获取数据: %(data_type)s")
            return self._data_cache[cache_key]

        try:
            if self.use_mock_data:
                # 使用Mock数据
                data = self._get_mock_data(data_type, **kwargs)
            else:
                # 使用真实数据库数据
                data = self._get_real_data(data_type, **kwargs)

            # 更新缓存
            self._update_cache(cache_key, data)

            return data

        except Exception:
            logger.error("获取数据失败 {data_type}: {str(e)}", exc_info=True)
            # 如果是真实数据获取失败，可以降级到Mock数据
            if not self.use_mock_data:
                logger.warning("降级到Mock数据: %(data_type)s")
                return self._get_mock_data(data_type, **kwargs)
            raise

    def _get_mock_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取Mock数据"""
        try:
            # 根据数据类型调用相应的Mock模块
            if data_type == "dashboard":
                from src.mock.mock_Dashboard import (
                    get_leading_sectors,
                    get_market_heat_data,
                    get_market_stats,
                )

                return {
                    "market_overview": {
                        "indices_count": 13,
                        "rising_count": 8,
                        "falling_count": 5,
                        "total_volume": 2800000000,
                        "market_cap": 85000000000000,
                    },
                    "market_stats": get_market_stats(),
                    "market_heat": get_market_heat_data(),
                    "leading_sectors": get_leading_sectors(),
                    "timestamp": datetime.now().isoformat(),
                }

            if data_type == "stocks":
                from src.mock.mock_Stocks import get_stock_list

                page = kwargs.get("page", 1)
                page_size = kwargs.get("page_size", 20)
                exchange = kwargs.get("exchange", "all")

                stocks = get_stock_list(params={"page": page, "page_size": page_size, "exchange": exchange})

                return {
                    "stocks": stocks,
                    "total": len(stocks),
                    "page": page,
                    "page_size": page_size,
                    "timestamp": datetime.now().isoformat(),
                }

            if data_type == "technical":
                try:
                    import sys

                    sys.path.append("/opt/claude/mystocks_spec")
                    sys.path.append("/opt/claude/mystocks_spec/src")
                    from src.mock.mock_TechnicalAnalysis import (
                        get_all_indicators,
                        get_momentum_indicators,
                        get_trading_signals,
                        get_trend_indicators,
                        get_volatility_indicators,
                        get_volume_indicators,
                    )
                except ImportError:
                    logger.error("导入Mock模块失败: %(e)s")

                    # 降级到默认实现
                    def get_all_indicators(symbol):
                        return {
                            "trend": {"ma5": 10.5, "ma10": 10.8, "ma20": 11.2},
                            "momentum": {"rsi6": 65.5, "rsi12": 58.2},
                            "volatility": {
                                "bb_upper": 12.5,
                                "bb_middle": 11.0,
                                "bb_lower": 9.5,
                            },
                            "volume": {"obv": 1250000, "vwap": 10.8},
                        }

                    def get_trend_indicators(symbol):
                        return {"ma5": 10.5}

                    def get_momentum_indicators(symbol):
                        return {"rsi6": 65.5}

                    def get_volatility_indicators(symbol):
                        return {"bb_upper": 12.5}

                    def get_volume_indicators(symbol):
                        return {"obv": 1250000}

                    def get_trading_signals(symbol):
                        return {"signal": "hold"}

                symbol = kwargs.get("symbol")

                if symbol:
                    indicators = get_all_indicators(symbol)
                    signals = get_trading_signals(symbol)
                else:
                    # 获取多个股票的指标
                    symbols = kwargs.get("symbols", ["000001", "000002", "600000"])
                    indicators = {}
                    signals = {}

                    for sym in symbols:
                        indicators[sym] = get_all_indicators(sym)
                        signals[sym] = get_trading_signals(sym)

                return {
                    "indicators": indicators,
                    "signals": signals,
                    "timestamp": datetime.now().isoformat(),
                }

            if data_type == "wencai":
                from src.mock.mock_Wencai import get_query_results, get_wencai_queries

                query_name = kwargs.get("query_name", "qs_1")

                if query_name == "all":
                    queries = get_wencai_queries()
                    return {
                        "queries": queries.get("queries", []),
                        "timestamp": datetime.now().isoformat(),
                    }
                query_result = get_query_results(query_name=query_name, limit=20, offset=0)
                return {
                    "query_result": query_result,
                    "timestamp": datetime.now().isoformat(),
                }

            if data_type == "strategy":
                from src.mock.mock_StrategyManagement import (
                    get_strategy_definitions,
                    get_strategy_results,
                )

                action = kwargs.get("action", "list")

                if action == "definitions":
                    strategies = get_strategy_definitions()
                    return {
                        "success": True,
                        "data": strategies.get("strategies", []),
                        "total": len(strategies.get("strategies", [])),
                        "timestamp": datetime.now().isoformat(),
                    }
                if action == "list":
                    strategies = get_strategy_definitions()
                    return {
                        "strategies": strategies.get("strategies", []),
                        "timestamp": datetime.now().isoformat(),
                    }
                if action == "run":
                    strategy_name = kwargs.get("strategy_name")
                    symbols = kwargs.get("symbols", [])

                    result = get_strategy_results(
                        request={
                            "strategy_name": strategy_name,
                            "symbols": symbols,
                            "start_date": kwargs.get("start_date"),
                            "end_date": kwargs.get("end_date"),
                        },
                    )
                    return {
                        "strategy_result": result,
                        "timestamp": datetime.now().isoformat(),
                    }

            elif data_type == "monitoring":
                from src.mock.mock_Dashboard import (
                    get_leading_sectors,
                )

                alert_type = kwargs.get("alert_type", "all")

                # 生成模拟的监控数据
                alerts = (
                    [
                        {
                            "id": f"alert_{i}",
                            "type": "price_change",
                            "symbol": f"00000{i}",
                            "message": f"股票 00000{i} 价格异常波动",
                            "timestamp": datetime.now().isoformat(),
                            "severity": "medium",
                        }
                        for i in range(5)
                    ]
                    if alert_type in ["all", "alerts"]
                    else []
                )

                dragon_tiger = get_leading_sectors() if alert_type in ["all", "dragon_tiger"] else []

                return {
                    "alerts": alerts,
                    "dragon_tiger": dragon_tiger,
                    "timestamp": datetime.now().isoformat(),
                }

            # 市场数据相关Mock
            elif data_type == "market_heatmap":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_Market import get_market_heatmap

                    market = kwargs.get("market", "cn")
                    limit = kwargs.get("limit", 50)

                    data = get_market_heatmap(market=market, limit=limit)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 如果无法导入，返回模拟数据
                    return {
                        "data": [
                            {
                                "symbol": f"60000{i}",
                                "name": f"股票{i:03d}",
                                "change": random.uniform(-5, 5),
                            }
                            for i in range(kwargs.get("limit", 50))
                        ],
                        "total": kwargs.get("limit", 50),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "real_time_quotes":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_Market import get_real_time_quotes

                    symbols = kwargs.get("symbols")

                    data = get_real_time_quotes(symbols=symbols)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [
                            {
                                "symbol": "000001",
                                "name": "平安银行",
                                "current": 15.32,
                                "change": 0.45,
                            },
                        ],
                        "total": 1,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "stock_list":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_Market import get_stock_list

                    limit = kwargs.get("limit", 100)
                    search = kwargs.get("search")
                    exchange = kwargs.get("exchange")
                    security_type = kwargs.get("security_type")

                    data = get_stock_list(
                        limit=limit,
                        search=search,
                        exchange=exchange,
                        security_type=security_type,
                    )
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [
                            {
                                "symbol": f"{i:06d}",
                                "name": f"股票{i:03d}",
                                "exchange": "SSE",
                            }
                            for i in range(kwargs.get("limit", 100))
                        ],
                        "total": kwargs.get("limit", 100),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            # 股票搜索相关Mock
            elif data_type == "stock_search":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_StockSearch import search_stocks

                    keyword = kwargs.get("keyword", "")
                    industry = kwargs.get("industry", "")
                    market = kwargs.get("market", "")
                    limit = kwargs.get("limit", 20)

                    data = search_stocks(keyword=keyword, industry=industry, market=market, limit=limit)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [
                            {
                                "symbol": "000001",
                                "description": "平安银行",
                                "displaySymbol": "000001.SZ",
                                "type": "Common Stock",
                                "exchange": "SZSE",
                            },
                            {
                                "symbol": "000002",
                                "description": "万科A",
                                "displaySymbol": "000002.SZ",
                                "type": "Common Stock",
                                "exchange": "SZSE",
                            },
                        ],
                        "total": 2,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "stock_quote":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_StockSearch import get_stock_detail

                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "cn")

                    data = get_stock_detail(symbol=symbol)
                    return {
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": {
                            "symbol": kwargs.get("symbol", "000001"),
                            "name": "平安银行",
                            "current": 15.32,
                            "change": 0.45,
                            "percent_change": 3.03,
                            "volume": 123456789,
                            "amount": 1890456789.45,
                            "open": 14.85,
                            "high": 15.55,
                            "low": 14.80,
                            "previous_close": 14.87,
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "stock_profile":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_StockSearch import get_stock_detail

                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "cn")

                    detail = get_stock_detail(symbol=symbol)
                    return {
                        "data": detail,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": {
                            "symbol": kwargs.get("symbol", "000001"),
                            "name": "平安银行",
                            "industry": "银行业",
                            "market_cap": 296786.54,
                            "listing_date": "1991-04-03",
                            "description": "平安银行股份有限公司是一家股份制商业银行...",
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "stock_news":
                symbol = kwargs.get("symbol")
                market = kwargs.get("market", "cn")

                # 生成模拟新闻数据
                news = [
                    {
                        "headline": f"{symbol} 最新财务报告发布",
                        "summary": f"股票 {symbol} 发布了最新的季度财务报告...",
                        "source": "财经网",
                        "datetime": datetime.now().timestamp(),
                        "url": f"https://example.com/news/{symbol}",
                        "image": None,
                        "category": "financial",
                    }
                    for i in range(5)
                ]

                return {
                    "data": news,
                    "timestamp": datetime.now().isoformat(),
                    "source": "mock",
                }

            elif data_type == "stock_recommendation":
                # 生成模拟分析师推荐数据
                symbol = kwargs.get("symbol")

                recommendation = {
                    "symbol": symbol,
                    "rating": "buy",
                    "target_price": round(random.uniform(50, 200), 2),
                    "current_price": round(random.uniform(40, 180), 2),
                    "analysts": [
                        {
                            "name": "张分析师",
                            "rating": "买入",
                            "target": round(random.uniform(50, 200), 2),
                        },
                        {
                            "name": "李分析师",
                            "rating": "持有",
                            "target": round(random.uniform(45, 190), 2),
                        },
                    ],
                }

                return {
                    "data": recommendation,
                    "timestamp": datetime.now().isoformat(),
                    "source": "mock",
                }

            # TradingView相关Mock
            elif data_type == "tradingview_chart":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_TradingView import get_chart_config

                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "CN")
                    interval = kwargs.get("interval", "D")
                    theme = kwargs.get("theme", "dark")
                    locale = kwargs.get("locale", "zh_CN")
                    container_id = kwargs.get("container_id", "tradingview_chart")

                    config = get_chart_config(
                        symbol=symbol,
                        market=market,
                        interval=interval,
                        theme=theme,
                        locale=locale,
                        container_id=container_id,
                    )
                    return {
                        "config": config,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟配置
                    return {
                        "config": {
                            "container_id": kwargs.get("container_id", "tradingview_chart"),
                            "symbol": kwargs.get("symbol", "AAPL"),
                            "theme": kwargs.get("theme", "dark"),
                            "locale": kwargs.get("locale", "zh_CN"),
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "tradingview_mini_chart":
                try:
                    import os
                    import sys

                    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
                    from src.mock.mock_TradingView import get_mini_chart_config

                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "CN")
                    theme = kwargs.get("theme", "dark")
                    locale = kwargs.get("locale", "zh_CN")
                    container_id = kwargs.get("container_id", "tradingview_mini_chart")

                    config = get_mini_chart_config(
                        symbol=symbol,
                        market=market,
                        theme=theme,
                        locale=locale,
                        container_id=container_id,
                    )
                    return {
                        "config": config,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }
                except ImportError:
                    # 返回模拟配置
                    return {
                        "config": {
                            "container_id": kwargs.get("container_id", "tradingview_mini_chart"),
                            "symbol": kwargs.get("symbol", "AAPL"),
                            "theme": kwargs.get("theme", "dark"),
                            "locale": kwargs.get("locale", "zh_CN"),
                            "width": "400px",
                            "height": "200px",
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock",
                    }

            elif data_type == "watchlist":
                return get_watchlist_mock_data(self, **kwargs)

            elif data_type == "fund-flow":
                return self._generate_mock_fund_flow(**kwargs)

            elif data_type == "backtest":
                return self._generate_mock_backtest_data(**kwargs)

            else:
                raise ValueError(f"不支持的数据类型: {data_type}")

        except ImportError:
            logger.error("导入Mock模块失败: {str(e)}")
            # 返回默认数据而不是抛出异常
            return self._get_default_data(data_type, **kwargs)
        except Exception:
            logger.error("获取Mock数据失败 {data_type}: {str(e)}", exc_info=True)
            # 返回默认数据而不是抛出异常
            return self._get_default_data(data_type, **kwargs)
