#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一的Mock数据管理系统

提供数据源切换和Mock数据管理的统一接口，支持环境变量控制的数据源切换。

作者: MyStocks Backend Team
创建日期: 2025-10-17
版本: 1.0.0
"""

import os
import logging
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)


class UnifiedMockDataManager:
    """统一Mock数据管理器"""
    
    def __init__(self, use_mock_data: bool = None):
        """
        初始化Mock数据管理器
        
        Args:
            use_mock_data: 是否使用Mock数据，如果为None则从环境变量读取
        """
        # 从环境变量获取数据源配置
        self.use_mock_data = use_mock_data or os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
        
        # Mock数据目录
        self.mock_data_dir = Path(__file__).parent
        
        # 数据缓存
        self._data_cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 300  # 5分钟缓存
        
        logger.info(f"初始化Mock数据管理器，使用Mock数据: {self.use_mock_data}")
    
    def get_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """
        获取统一数据接口
        
        Args:
            data_type: 数据类型 (dashboard, stocks, technical, wencai, strategy, monitoring)
            **kwargs: 额外的查询参数
            
        Returns:
            数据响应
        """
        cache_key = f"{data_type}:{str(kwargs)}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            logger.debug(f"从缓存获取数据: {data_type}")
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
            
        except Exception as e:
            logger.error(f"获取数据失败 {data_type}: {str(e)}", exc_info=True)
            # 如果是真实数据获取失败，可以降级到Mock数据
            if not self.use_mock_data:
                logger.warning(f"降级到Mock数据: {data_type}")
                return self._get_mock_data(data_type, **kwargs)
            else:
                raise
    
    def _get_mock_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取Mock数据"""
        try:
            # 根据数据类型调用相应的Mock模块
            if data_type == "dashboard":
                from src.mock.mock_Dashboard import get_market_stats, get_market_heat_data, get_leading_sectors
                
                return {
                    "market_overview": {
                        "indices_count": 13,
                        "rising_count": 8,
                        "falling_count": 5,
                        "total_volume": 2800000000,
                        "market_cap": 85000000000000
                    },
                    "market_stats": get_market_stats(),
                    "market_heat": get_market_heat_data(),
                    "leading_sectors": get_leading_sectors(),
                    "timestamp": datetime.now().isoformat()
                }
            
            elif data_type == "stocks":
                from src.mock.mock_Stocks import get_stock_list, get_real_time_quote
                
                page = kwargs.get("page", 1)
                page_size = kwargs.get("page_size", 20)
                exchange = kwargs.get("exchange", "all")
                
                stocks = get_stock_list(params={"page": page, "page_size": page_size, "exchange": exchange})
                
                return {
                    "stocks": stocks,
                    "total": len(stocks),
                    "page": page,
                    "page_size": page_size,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif data_type == "technical":
                from src.mock.mock_TechnicalAnalysis import get_technical_indicators, get_signal_analysis
                
                symbol = kwargs.get("symbol")
                
                if symbol:
                    indicators = get_technical_indicators(symbol=symbol, indicators=["MA", "MACD", "RSI"])
                    signals = get_signal_analysis(symbol=symbol, days=30)
                else:
                    # 获取多个股票的指标
                    symbols = kwargs.get("symbols", ["000001", "000002", "600000"])
                    indicators = {}
                    signals = {}
                    
                    for sym in symbols:
                        indicators[sym] = get_technical_indicators(symbol=sym, indicators=["MA", "MACD", "RSI"])
                        signals[sym] = get_signal_analysis(symbol=sym, days=30).to_dict("records")
                
                return {
                    "indicators": indicators,
                    "signals": signals,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif data_type == "wencai":
                from src.mock.mock_Wencai import get_wencai_queries, get_query_results
                
                query_name = kwargs.get("query_name", "qs_1")
                
                if query_name == "all":
                    queries = get_wencai_queries()
                    return {
                        "queries": queries.get("queries", []),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    query_result = get_query_results(query_name=query_name, limit=20, offset=0)
                    return {
                        "query_result": query_result,
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif data_type == "strategy":
                from src.mock.mock_StrategyManagement import get_strategy_definitions, get_strategy_results
                
                action = kwargs.get("action", "list")
                
                if action == "list":
                    strategies = get_strategy_definitions()
                    return {
                        "strategies": strategies.get("strategies", []),
                        "timestamp": datetime.now().isoformat()
                    }
                elif action == "run":
                    strategy_name = kwargs.get("strategy_name")
                    symbols = kwargs.get("symbols", [])
                    
                    result = get_strategy_results(
                        request={
                            "strategy_name": strategy_name,
                            "symbols": symbols,
                            "start_date": kwargs.get("start_date"),
                            "end_date": kwargs.get("end_date")
                        }
                    )
                    return {
                        "strategy_result": result,
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif data_type == "monitoring":
                from src.mock.mock_Dashboard import get_market_stats, get_leading_sectors
                
                alert_type = kwargs.get("alert_type", "all")
                
                # 生成模拟的监控数据
                alerts = [
                    {
                        "id": f"alert_{i}",
                        "type": "price_change",
                        "symbol": f"00000{i}",
                        "message": f"股票 00000{i} 价格异常波动",
                        "timestamp": datetime.now().isoformat(),
                        "severity": "medium"
                    } for i in range(5)
                ] if alert_type in ["all", "alerts"] else []
                
                dragon_tiger = get_leading_sectors() if alert_type in ["all", "dragon_tiger"] else []
                
                return {
                    "alerts": alerts,
                    "dragon_tiger": dragon_tiger,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 市场数据相关Mock
            elif data_type == "market_heatmap":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_Market import get_market_heatmap
                    
                    market = kwargs.get("market", "cn")
                    limit = kwargs.get("limit", 50)
                    
                    data = get_market_heatmap(market=market, limit=limit)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
                except ImportError:
                    # 如果无法导入，返回模拟数据
                    return {
                        "data": [{"symbol": f"60000{i}", "name": f"股票{i:03d}", "change": random.uniform(-5, 5)} for i in range(kwargs.get("limit", 50))],
                        "total": kwargs.get("limit", 50),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "real_time_quotes":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_Market import get_real_time_quotes
                    
                    symbols = kwargs.get("symbols")
                    
                    data = get_real_time_quotes(symbols=symbols)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [{"symbol": "000001", "name": "平安银行", "current": 15.32, "change": 0.45}],
                        "total": 1,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "stock_list":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_Market import get_stock_list
                    
                    limit = kwargs.get("limit", 100)
                    search = kwargs.get("search")
                    exchange = kwargs.get("exchange")
                    security_type = kwargs.get("security_type")
                    
                    data = get_stock_list(limit=limit, search=search, exchange=exchange, security_type=security_type)
                    return {
                        "data": data,
                        "total": len(data),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [{"symbol": f"{i:06d}", "name": f"股票{i:03d}", "exchange": "SSE"} for i in range(kwargs.get("limit", 100))],
                        "total": kwargs.get("limit", 100),
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            # 股票搜索相关Mock
            elif data_type == "stock_search":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
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
                        "source": "mock"
                    }
                except ImportError:
                    # 返回模拟数据
                    return {
                        "data": [
                            {
                                "symbol": f"000001",
                                "description": "平安银行",
                                "displaySymbol": "000001.SZ",
                                "type": "Common Stock",
                                "exchange": "SZSE"
                            },
                            {
                                "symbol": f"000002",
                                "description": "万科A",
                                "displaySymbol": "000002.SZ", 
                                "type": "Common Stock",
                                "exchange": "SZSE"
                            }
                        ],
                        "total": 2,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "stock_quote":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_StockSearch import get_stock_detail
                    
                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "cn")
                    
                    data = get_stock_detail(symbol=symbol)
                    return {
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
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
                            "previous_close": 14.87
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "stock_profile":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_StockSearch import get_stock_detail
                    
                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "cn")
                    
                    detail = get_stock_detail(symbol=symbol)
                    return {
                        "data": detail,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
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
                            "description": "平安银行股份有限公司是一家股份制商业银行..."
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "stock_news":
                from src.mock.mock_StockSearch import get_stock_concept
                
                symbol = kwargs.get("symbol")
                market = kwargs.get("market", "cn")
                days = kwargs.get("days", 7)
                
                # 生成模拟新闻数据
                news = [
                    {
                        "headline": f"{symbol} 最新财务报告发布",
                        "summary": f"股票 {symbol} 发布了最新的季度财务报告...",
                        "source": "财经网",
                        "datetime": datetime.now().timestamp(),
                        "url": f"https://example.com/news/{symbol}",
                        "image": None,
                        "category": "financial"
                    } for i in range(5)
                ]
                
                return {
                    "data": news,
                    "timestamp": datetime.now().isoformat(),
                    "source": "mock"
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
                        {"name": "张分析师", "rating": "买入", "target": round(random.uniform(50, 200), 2)},
                        {"name": "李分析师", "rating": "持有", "target": round(random.uniform(45, 190), 2)}
                    ]
                }
                
                return {
                    "data": recommendation,
                    "timestamp": datetime.now().isoformat(),
                    "source": "mock"
                }
            
            # TradingView相关Mock
            elif data_type == "tradingview_chart":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_TradingView import get_chart_config
                    
                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "CN")
                    interval = kwargs.get("interval", "D")
                    theme = kwargs.get("theme", "dark")
                    locale = kwargs.get("locale", "zh_CN")
                    container_id = kwargs.get("container_id", "tradingview_chart")
                    
                    config = get_chart_config(symbol=symbol, market=market, interval=interval, 
                                            theme=theme, locale=locale, container_id=container_id)
                    return {
                        "config": config,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
                except ImportError:
                    # 返回模拟配置
                    return {
                        "config": {
                            "container_id": kwargs.get("container_id", "tradingview_chart"),
                            "symbol": kwargs.get("symbol", "AAPL"),
                            "theme": kwargs.get("theme", "dark"),
                            "locale": kwargs.get("locale", "zh_CN")
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            elif data_type == "tradingview_mini_chart":
                try:
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                    from src.mock.mock_TradingView import get_mini_chart_config
                    
                    symbol = kwargs.get("symbol")
                    market = kwargs.get("market", "CN")
                    theme = kwargs.get("theme", "dark")
                    locale = kwargs.get("locale", "zh_CN")
                    container_id = kwargs.get("container_id", "tradingview_mini_chart")
                    
                    config = get_mini_chart_config(symbol=symbol, market=market, theme=theme, 
                                                 locale=locale, container_id=container_id)
                    return {
                        "config": config,
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
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
                            "height": "200px"
                        },
                        "timestamp": datetime.now().isoformat(),
                        "source": "mock"
                    }
            
            else:
                raise ValueError(f"不支持的数据类型: {data_type}")
                
        except ImportError as e:
            logger.error(f"导入Mock模块失败: {str(e)}")
            raise ValueError(f"Mock模块导入失败: {data_type}")
        except Exception as e:
            logger.error(f"获取Mock数据失败 {data_type}: {str(e)}", exc_info=True)
            raise
    
    def _get_real_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """获取真实数据库数据"""
        # 这里应该连接真实的数据库
        # 暂时抛出异常，提示需要实现真实数据获取逻辑
        raise NotImplementedError(f"真实数据库数据获取功能尚未实现: {data_type}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._cache_timestamp:
            return False
        
        timestamp = self._cache_timestamp[cache_key]
        return (datetime.now() - timestamp).total_seconds() < self._cache_ttl
    
    def _update_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """更新缓存"""
        self._data_cache[cache_key] = data
        self._cache_timestamp[cache_key] = datetime.now()
        
        # 缓存大小限制
        if len(self._data_cache) > 1000:
            # 清理最旧的缓存
            oldest_key = min(self._cache_timestamp.keys(), 
                           key=lambda k: self._cache_timestamp[k])
            del self._data_cache[oldest_key]
            del self._cache_timestamp[oldest_key]
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._data_cache.clear()
        self._cache_timestamp.clear()
        logger.info("缓存已清除")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self._data_cache),
            "cache_ttl": self._cache_ttl,
            "mock_mode": self.use_mock_data
        }
    
    def set_mock_mode(self, enabled: bool) -> None:
        """设置Mock模式"""
        self.use_mock_data = enabled
        logger.info(f"设置Mock模式: {enabled}")
        
        # 切换模式时清除缓存
        self.clear_cache()


# 创建全局Mock数据管理器实例
mock_data_manager = UnifiedMockDataManager()


def get_mock_data_manager() -> UnifiedMockDataManager:
    """获取Mock数据管理器实例"""
    return mock_data_manager


# 便利函数
def get_dashboard_data() -> Dict[str, Any]:
    """获取Dashboard数据"""
    return mock_data_manager.get_data("dashboard")


def get_stocks_data(page: int = 1, page_size: int = 20, exchange: str = "all") -> Dict[str, Any]:
    """获取股票数据"""
    return mock_data_manager.get_data("stocks", page=page, page_size=page_size, exchange=exchange)


def get_technical_data(symbol: str = None, symbols: List[str] = None) -> Dict[str, Any]:
    """获取技术指标数据"""
    return mock_data_manager.get_data("technical", symbol=symbol, symbols=symbols)


def get_wencai_data(query_name: str = "all") -> Dict[str, Any]:
    """获取问财数据"""
    return mock_data_manager.get_data("wencai", query_name=query_name)


def get_strategy_data(action: str = "list", **kwargs) -> Dict[str, Any]:
    """获取策略数据"""
    return mock_data_manager.get_data("strategy", action=action, **kwargs)


def get_monitoring_data(alert_type: str = "all") -> Dict[str, Any]:
    """获取监控数据"""
    return mock_data_manager.get_data("monitoring", alert_type=alert_type)


# 数据源切换装饰器
def data_source_toggle(func):
    """数据源切换装饰器"""
    def wrapper(*args, **kwargs):
        try:
            # 尝试使用真实数据
            return func(*args, **kwargs)
        except NotImplementedError:
            # 如果真实数据不可用，降级到Mock数据
            logger.warning(f"数据源切换: {func.__name__} 降级到Mock数据")
            mock_manager = get_mock_data_manager()
            mock_manager.set_mock_mode(True)
            
            # 重新尝试调用原始函数
            return func(*args, **kwargs)
    
    return wrapper


if __name__ == "__main__":
    # 测试代码
    manager = UnifiedMockDataManager(use_mock_data=True)
    
    # 测试获取Dashboard数据
    dashboard_data = manager.get_data("dashboard")
    print("Dashboard数据测试:")
    print(f"市场概览: {dashboard_data['market_overview']['indices_count']} 个指数")
    print(f"市场统计: {dashboard_data['market_stats']['total_market_cap']}")
    
    # 测试获取股票数据
    stocks_data = manager.get_data("stocks", page=1, page_size=5)
    print(f"\n股票数据测试: 页面 {stocks_data['page']}, 总计 {stocks_data['total']} 条记录")
    
    # 获取缓存信息
    cache_info = manager.get_cache_info()
    print(f"\n缓存信息: {cache_info}")
