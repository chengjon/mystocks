"""
Mock数据源实现类
封装现有的Mock函数，适配统一接口标准
"""

from typing import Dict, List, Optional, Union
import pandas as pd
from src.interfaces.data_source_interface import DataSourceInterface
from src.mock import (
    mock_Stocks,
    mock_TechnicalAnalysis,
    mock_RealTimeMonitor,
    mock_Wencai,
    mock_StrategyManagement,
    mock_IndicatorLibrary,
)
from src.database.mock_data_storage import mock_data_storage


class MockDataSource(DataSourceInterface):
    """
    Mock数据源实现类
    封装现有的Mock函数，适配统一接口标准
    """

    def __init__(self):
        """初始化Mock数据源"""
        self.storage = mock_data_storage

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表"""
        stock_list = mock_Stocks.get_stock_list(params)
        # 模拟数据落地
        if stock_list:
            self.storage.insert_stock_info(stock_list)
        return stock_list

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息"""
        # Mock Stocks模块没有直接的get_stock_detail函数，使用get_real_time_quote作为替代
        quote = mock_Stocks.get_real_time_quote(stock_code)
        result = {
            "symbol": quote.get("symbol", stock_code),
            "name": quote.get("name", f"股票{stock_code}"),
            "industry": quote.get("industry", ""),
            "area": quote.get("area", ""),
            "market": quote.get("market", ""),
            "list_date": quote.get("list_date", ""),
        }
        # 模拟数据落地
        self.storage.insert_stock_info([result])
        return result

    def get_real_time_quote(self, stock_code: str) -> Dict:
        """获取实时行情"""
        quotes = mock_Stocks.get_real_time_quote([stock_code] if isinstance(stock_code, str) else stock_code)
        quote = quotes[0] if isinstance(quotes, list) and quotes else {}
        # 模拟数据落地
        if quote:
            # 转换数据格式以匹配存储要求
            storage_data = {
                "symbol": quote.get("symbol"),
                "trade_time": quote.get("timestamp"),
                "open": quote.get("open"),
                "high": quote.get("high"),
                "low": quote.get("low"),
                "close": quote.get("price"),
                "volume": quote.get("volume"),
                "amount": quote.get("turnover"),
                "pre_close": quote.get("close"),
                "change": quote.get("change"),
                "change_pct": quote.get("change_pct"),
                "turnover_rate": None,  # Mock数据中没有这个字段
                "pe_ratio": None,  # Mock数据中没有这个字段
                "pb_ratio": None,  # Mock数据中没有这个字段
            }
            self.storage.insert_realtime_quotes([storage_data])
        return quote

    def get_history_profit(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取历史收益"""
        return mock_Stocks.get_history_profit(stock_code, days)

    def get_technical_indicators(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """获取技术指标"""
        # Mock TechnicalAnalysis模块可能没有完全匹配的函数，这里使用get_all_indicators作为替代
        all_indicators = mock_TechnicalAnalysis.get_all_indicators(stock_code)
        # 将单一指标转换为时间序列格式
        if all_indicators:
            result = [
                {
                    "symbol": stock_code,
                    "date": start_date,  # 使用开始日期作为模拟日期
                    "trend": all_indicators.get("trend", {}),
                    "momentum": all_indicators.get("momentum", {}),
                    "volatility": all_indicators.get("volatility", {}),
                    "volume": all_indicators.get("volume", {}),
                }
            ]

            # 模拟数据落地 - 将技术指标转换为存储格式
            storage_data = []
            for indicator_type, indicators in all_indicators.items():
                if isinstance(indicators, dict):
                    for name, value in indicators.items():
                        # 处理嵌套字典
                        if isinstance(value, dict):
                            # 如果值是字典，将其作为单独的指标存储
                            for sub_name, sub_value in value.items():
                                storage_data.append(
                                    {
                                        "symbol": stock_code,
                                        "calc_date": start_date,
                                        "indicator_name": f"{indicator_type}_{name}_{sub_name}",
                                        "indicator_value": sub_value if isinstance(sub_value, (int, float)) else 0.0,
                                        "indicator_params": {},
                                    }
                                )
                        else:
                            # 如果值不是字典，直接存储
                            storage_data.append(
                                {
                                    "symbol": stock_code,
                                    "calc_date": start_date,
                                    "indicator_name": f"{indicator_type}_{name}",
                                    "indicator_value": value if isinstance(value, (int, float)) else 0.0,
                                    "indicator_params": {},
                                }
                            )

            if storage_data:
                self.storage.insert_technical_indicators(storage_data)

            return result
        return []

    def get_all_indicators(self, stock_code: str) -> Dict:
        """获取所有技术指标"""
        return mock_TechnicalAnalysis.get_all_indicators(stock_code)

    def get_trend_indicators(self, stock_code: str) -> Dict:
        """获取趋势指标"""
        return mock_TechnicalAnalysis.get_trend_indicators(stock_code)

    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """获取动量指标"""
        return mock_TechnicalAnalysis.get_momentum_indicators(stock_code)

    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """获取波动率指标"""
        return mock_TechnicalAnalysis.get_volatility_indicators(stock_code)

    def get_volume_indicators(self, stock_code: str) -> Dict:
        """获取成交量指标"""
        return mock_TechnicalAnalysis.get_volume_indicators(stock_code)

    def get_trading_signals(self, stock_code: str) -> Dict:
        """获取交易信号"""
        return mock_TechnicalAnalysis.get_trading_signals(stock_code)

    def get_kline_data(self, stock_code: str) -> Dict:
        """获取K线历史数据"""
        return mock_TechnicalAnalysis.get_kline_data(stock_code)

    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """获取形态识别结果"""
        return mock_TechnicalAnalysis.get_pattern_recognition(stock_code)

    def get_realtime_alerts(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取实时告警"""
        return mock_RealTimeMonitor.get_realtime_alerts(params)

    def get_monitoring_summary(self) -> Dict:
        """获取监控摘要"""
        return mock_RealTimeMonitor.get_monitoring_summary()

    def get_monitoring_status(self) -> Dict:
        """获取监控状态"""
        return mock_RealTimeMonitor.get_monitoring_status()

    def get_market_monitoring(self) -> Dict:
        """获取市场监控数据"""
        return mock_RealTimeMonitor.get_monitoring_summary()

    def get_wencai_queries(self) -> Dict:
        """获取预定义查询列表"""
        return mock_Wencai.get_wencai_queries()

    def execute_query(self, request: Dict) -> Dict:
        """执行预定义查询"""
        return mock_Wencai.execute_query(request)

    def execute_custom_query(self, request: Dict) -> Dict:
        """执行自定义查询"""
        return mock_Wencai.execute_custom_query(request)

    def get_query_results(self, query_name: str, limit: int = 20, offset: int = 0) -> Dict:
        """获取查询结果"""
        return mock_Wencai.get_query_results(query_name, limit, offset)

    def get_strategy_definitions(self) -> Dict:
        """获取策略定义列表"""
        return mock_StrategyManagement.get_strategy_definitions()

    def run_strategy_single(self, request: Dict) -> Dict:
        """单策略运行"""
        return mock_StrategyManagement.run_strategy_single(request)

    def run_strategy_batch(self, request: Dict) -> Dict:
        """批量策略运行"""
        return mock_StrategyManagement.run_strategy_batch(request)

    def get_strategy_results(self, request: Dict) -> Dict:
        """获取策略结果"""
        return mock_StrategyManagement.get_strategy_results(request)

    def get_matched_stocks(self, request: Dict) -> Dict:
        """获取匹配的股票"""
        return mock_StrategyManagement.get_matched_stocks(request)

    def get_strategy_stats(self) -> Dict:
        """获取策略统计"""
        return mock_StrategyManagement.get_strategy_stats()

    def get_indicator_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取指标列表"""
        return mock_IndicatorLibrary.get_indicator_list(params)

    def get_indicator_detail(self, indicator_id: str) -> Dict:
        """获取指标详情"""
        return mock_IndicatorLibrary.get_indicator_detail(indicator_id)

    def get_indicator_data(self, indicator_id: str, symbol: str, days: int = 30) -> pd.DataFrame:
        """获取指标数据表格"""
        return mock_IndicatorLibrary.get_indicator_data(indicator_id, symbol, days)

    def get_data_from_adapter(self, adapter_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """从指定适配器获取数据（统一适配器调用入口）"""
        # Mock模式下返回模拟数据
        return {
            "adapter_type": adapter_type,
            "method": method,
            "params": kwargs,
            "data": "mock_data",
        }

    def get_data_with_failover(self, data_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """使用故障转移机制获取数据"""
        # Mock模式下返回模拟数据
        return {
            "data_type": data_type,
            "method": method,
            "params": kwargs,
            "data": "mock_data_with_failover",
        }
