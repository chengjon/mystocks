"""
真实数据源实现类
对接数据库，适配统一接口标准
"""

import logging
from typing import Dict, List, Optional, Union

import pandas as pd

from src.database.database_service import db_service
from src.interfaces.data_source_interface import DataSourceInterface

# 设置日志
logger = logging.getLogger(__name__)


class RealDataSource(DataSourceInterface):
    """
    真实数据源实现类
    对接数据库，适配统一接口标准
    """

    def _safe_call(self, method_name: str, method, *args, **kwargs):
        """
        安全调用数据库方法，处理连接异常

        Args:
            method_name: 方法名称（用于日志）
            method: 要调用的方法
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            方法调用结果或默认值
        """
        try:
            return method(*args, **kwargs)
        except Exception as e:
            logger.error("调用 %s 失败: %s", method_name, str(e))
            # 根据返回类型返回合适的默认值
            if method_name in ["get_stock_list", "get_realtime_alerts"]:
                return []
            elif method_name in ["get_history_profit", "get_indicator_data"]:
                return pd.DataFrame()
            else:
                return {}

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表"""
        return self._safe_call("get_stock_list", db_service.get_stock_list, params)

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息"""
        return self._safe_call("get_stock_detail", db_service.get_stock_detail, stock_code)

    def get_real_time_quote(self, stock_code: str) -> Dict:
        """获取实时行情"""
        quotes = self._safe_call("get_realtime_quotes", db_service.get_realtime_quotes, [stock_code])
        return quotes[0] if isinstance(quotes, list) and quotes else {}

    def get_technical_indicators(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """获取技术指标"""
        params = {"symbol": stock_code, "start_date": start_date, "end_date": end_date}
        return self._safe_call("get_technical_indicators", db_service.get_technical_indicators, params)

    def get_history_profit(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取历史收益"""
        # 暂时返回空DataFrame，后续实现
        return pd.DataFrame()

    def get_all_indicators(self, stock_code: str) -> Dict:
        """获取所有技术指标"""
        return self._safe_call(
            "get_all_indicators",
            db_service.get_all_indicators,
            {"stock_code": stock_code},
        )

    def get_trend_indicators(self, stock_code: str) -> Dict:
        """获取趋势指标"""
        return self._safe_call("get_trend_indicators", db_service.get_trend_indicators, stock_code)

    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """获取动量指标"""
        return self._safe_call("get_momentum_indicators", db_service.get_momentum_indicators, stock_code)

    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """获取波动率指标"""
        return self._safe_call(
            "get_volatility_indicators",
            db_service.get_volatility_indicators,
            stock_code,
        )

    def get_volume_indicators(self, stock_code: str) -> Dict:
        """获取成交量指标"""
        return self._safe_call("get_volume_indicators", db_service.get_volume_indicators, stock_code)

    def get_trading_signals(self, stock_code: str) -> Dict:
        """获取交易信号"""
        return self._safe_call("get_trading_signals", db_service.get_trading_signals, stock_code)

    def get_kline_data(self, stock_code: str) -> Dict:
        """获取K线历史数据"""
        return self._safe_call("get_stock_history", db_service.get_stock_history, {"symbol": stock_code})

    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """获取形态识别结果"""
        return self._safe_call("get_pattern_recognition", db_service.get_pattern_recognition, stock_code)

    def get_realtime_alerts(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取实时告警"""
        return self._safe_call("get_monitoring_alerts", db_service.get_monitoring_alerts, params)

    def get_monitoring_summary(self) -> Dict:
        """获取监控摘要"""
        return self._safe_call("get_monitoring_summary", db_service.get_monitoring_summary)

    def get_monitoring_status(self) -> Dict:
        """获取监控状态"""
        return self._safe_call("get_monitoring_status", db_service.get_monitoring_status)

    def get_market_monitoring(self) -> Dict:
        """获取市场监控数据"""
        return self._safe_call("get_market_monitoring", db_service.get_market_monitoring)

    def get_wencai_queries(self) -> Dict:
        """获取预定义查询列表"""
        # 暂时返回空字典，后续实现
        return {"queries": [], "total": 0}

    def execute_query(self, request: Dict) -> Dict:
        """执行预定义查询"""
        return self._safe_call("execute_wencai_query", db_service.execute_wencai_query, request)

    def execute_custom_query(self, request: Dict) -> Dict:
        """执行自定义查询"""
        return self._safe_call("execute_wencai_query", db_service.execute_wencai_query, request)

    def get_query_results(self, query_name: str, limit: int = 20, offset: int = 0) -> Dict:
        """获取查询结果"""
        params = {"query_name": query_name, "limit": limit, "offset": offset}
        return self._safe_call("execute_wencai_query", db_service.execute_wencai_query, params)

    def get_strategy_definitions(self) -> Dict:
        """获取策略定义列表"""
        return self._safe_call("get_strategy_definitions", db_service.get_strategy_definitions)

    def run_strategy_single(self, request: Dict) -> Dict:
        """单策略运行"""
        # 暂时返回空字典，后续实现
        return {}

    def run_strategy_batch(self, request: Dict) -> Dict:
        """批量策略运行"""
        # 暂时返回空字典，后续实现
        return {}

    def get_strategy_results(self, request: Dict) -> Dict:
        """获取策略结果"""
        return self._safe_call("get_strategy_results", db_service.get_strategy_results, request)

    def get_matched_stocks(self, request: Dict) -> Dict:
        """获取匹配的股票"""
        # 暂时返回空字典，后续实现
        return {}

    def get_strategy_stats(self) -> Dict:
        """获取策略统计"""
        return self._safe_call("get_strategy_performance", db_service.get_strategy_performance)

    def get_indicator_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取指标列表"""
        # 暂时返回空列表，后续实现
        return []

    def get_indicator_detail(self, indicator_id: str) -> Dict:
        """获取指标详情"""
        # 暂时返回空字典，后续实现
        return {}

    def get_indicator_data(self, indicator_id: str, symbol: str, days: int = 30) -> pd.DataFrame:
        """获取指标数据表格"""
        return self._safe_call(
            "get_indicator_data",
            db_service.get_indicator_data,
            indicator_id,
            symbol,
            days,
        )

    def get_data_from_adapter(self, adapter_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """从指定适配器获取数据（统一适配器调用入口）"""
        return self._safe_call(
            "get_data_from_adapter",
            db_service.get_data_from_adapter,
            adapter_type,
            method,
            **kwargs,
        )

    def get_data_with_failover(self, data_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """使用故障转移机制获取数据"""
        return self._safe_call(
            "get_data_with_failover",
            db_service.get_data_with_failover,
            data_type,
            method,
            **kwargs,
        )

    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取分钟K线数据"""
        # 直接从数据库服务获取数据
        return self._safe_call(
            "get_minute_kline",
            db_service.get_minute_kline,
            symbol,
            period,
            start_date,
            end_date,
        )

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据"""
        # 直接从数据库服务获取数据
        return self._safe_call("get_industry_classify", db_service.get_industry_classify)

    def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据"""
        # 直接从数据库服务获取数据
        return self._safe_call("get_concept_classify", db_service.get_concept_classify)

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """获取个股的行业和概念分类信息"""
        # 直接从数据库服务获取数据
        return self._safe_call("get_stock_industry_concept", db_service.get_stock_industry_concept, symbol)
