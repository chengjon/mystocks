"""
数据源接口定义 - 统一接口标准
定义所有数据源必须实现的方法和返回格式
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd


class DataSourceInterface(ABC):
    """
    数据源统一接口
    所有数据源实现类必须继承此接口并实现所有方法
    """
    
    @abstractmethod
    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        获取股票列表
        
        Args:
            params: Dict - 查询参数：
                    exchange: Optional[str] - 交易所筛选
                    limit: int - 每页数量，默认20
                    offset: int - 偏移量，默认0
        
        Returns:
            List[Dict]: 股票列表数据
        """
        pass
    
    @abstractmethod
    def get_stock_detail(self, stock_code: str) -> Dict:
        """
        获取股票详细信息
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 股票详细信息
        """
        pass
    
    @abstractmethod
    def get_real_time_quote(self, stock_code: str) -> Dict:
        """
        获取实时行情
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 实时行情数据
        """
        pass
    
    @abstractmethod
    def get_history_profit(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """
        获取历史收益
        
        Args:
            stock_code: str - 股票代码
            days: int - 天数，默认30天
            
        Returns:
            pd.DataFrame: 历史收益数据
        """
        pass
    
    @abstractmethod
    def get_technical_indicators(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """
        获取技术指标
        
        Args:
            stock_code: str - 股票代码
            start_date: str - 开始日期
            end_date: str - 结束日期
            
        Returns:
            List[Dict]: 技术指标数据列表
        """
        pass
    
    @abstractmethod
    def get_all_indicators(self, stock_code: str) -> Dict:
        """
        获取所有技术指标
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 所有技术指标数据
        """
        pass
    
    @abstractmethod
    def get_trend_indicators(self, stock_code: str) -> Dict:
        """
        获取趋势指标
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 趋势指标数据
        """
        pass
    
    @abstractmethod
    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """
        获取动量指标
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 动量指标数据
        """
        pass
    
    @abstractmethod
    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """
        获取波动率指标
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 波动率指标数据
        """
        pass
    
    @abstractmethod
    def get_volume_indicators(self, stock_code: str) -> Dict:
        """
        获取成交量指标
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 成交量指标数据
        """
        pass
    
    @abstractmethod
    def get_trading_signals(self, stock_code: str) -> Dict:
        """
        获取交易信号
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 交易信号数据
        """
        pass
    
    @abstractmethod
    def get_kline_data(self, stock_code: str) -> Dict:
        """
        获取K线历史数据
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: K线历史数据
        """
        pass
    
    @abstractmethod
    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """
        获取形态识别结果
        
        Args:
            stock_code: str - 股票代码
            
        Returns:
            Dict: 形态识别结果
        """
        pass
    
    @abstractmethod
    def get_realtime_alerts(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        获取实时告警
        
        Args:
            params: Dict - 查询参数：
                    limit: int - 返回记录数，默认50
                    offset: int - 偏移量，默认0
                    is_read: bool - 是否已读，None表示全部
        
        Returns:
            List[Dict]: 实时告警数据
        """
        pass
    
    @abstractmethod
    def get_monitoring_summary(self) -> Dict:
        """
        获取监控摘要
        
        Returns:
            Dict: 监控摘要数据
        """
        pass
    
    @abstractmethod
    def get_monitoring_status(self) -> Dict:
        """
        获取监控状态
        
        Returns:
            Dict: 监控状态信息
        """
        pass
    
    @abstractmethod
    def get_market_monitoring(self) -> Dict:
        """
        获取市场监控数据
        
        Returns:
            Dict: 市场监控数据
        """
        pass
    
    @abstractmethod
    def get_wencai_queries(self) -> Dict:
        """
        获取预定义查询列表
        
        Returns:
            Dict: 预定义查询列表
        """
        pass
    
    @abstractmethod
    def execute_query(self, request: Dict) -> Dict:
        """
        执行预定义查询
        
        Args:
            request: Dict - 请求参数：
                    query_name: str - 查询名称
                    pages: int - 页数
        
        Returns:
            Dict: 查询执行结果
        """
        pass
    
    @abstractmethod
    def execute_custom_query(self, request: Dict) -> Dict:
        """
        执行自定义查询
        
        Args:
            request: Dict - 请求参数：
                    query_text: str - 自定义查询文本
                    pages: int - 页数
        
        Returns:
            Dict: 自定义查询结果
        """
        pass
    
    @abstractmethod
    def get_query_results(self, query_name: str, limit: int = 20, offset: int = 0) -> Dict:
        """
        获取查询结果
        
        Args:
            query_name: str - 查询名称
            limit: int - 每页数量
            offset: int - 偏移量
        
        Returns:
            Dict: 查询结果数据
        """
        pass
    
    @abstractmethod
    def get_strategy_definitions(self) -> Dict:
        """
        获取策略定义列表
        
        Returns:
            Dict: 策略定义列表
        """
        pass
    
    @abstractmethod
    def run_strategy_single(self, request: Dict) -> Dict:
        """
        单策略运行
        
        Args:
            request: Dict - 请求参数：
                    strategy_code: str - 策略代码
                    parameters: Dict - 策略参数
                    date_range: Dict - 日期范围
        
        Returns:
            Dict: 策略运行结果
        """
        pass
    
    @abstractmethod
    def run_strategy_batch(self, request: Dict) -> Dict:
        """
        批量策略运行
        
        Args:
            request: Dict - 请求参数：
                    strategy_codes: List[str] - 策略代码列表
                    parameters: Dict - 策略参数
                    date_range: Dict - 日期范围
        
        Returns:
            Dict: 批量策略运行结果
        """
        pass
    
    @abstractmethod
    def get_strategy_results(self, request: Dict) -> Dict:
        """
        获取策略结果
        
        Args:
            request: Dict - 请求参数：
                    strategy_code: str - 策略代码
                    limit: int - 限制数量
                    offset: int - 偏移量
        
        Returns:
            Dict: 策略结果数据
        """
        pass
    
    @abstractmethod
    def get_matched_stocks(self, request: Dict) -> Dict:
        """
        获取匹配的股票
        
        Args:
            request: Dict - 请求参数：
                    strategy_code: str - 策略代码
                    filters: Dict - 筛选条件
        
        Returns:
            Dict: 匹配股票数据
        """
        pass
    
    @abstractmethod
    def get_strategy_stats(self) -> Dict:
        """
        获取策略统计
        
        Returns:
            Dict: 策略统计数据
        """
        pass
    
    @abstractmethod
    def get_indicator_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        获取指标列表
        
        Args:
            params: Dict - 查询参数：
                    category: Optional[str] - 指标分类
                    limit: int - 每页数量
                    offset: int - 偏移量
        
        Returns:
            List[Dict]: 指标列表
        """
        pass
    
    @abstractmethod
    def get_indicator_detail(self, indicator_id: str) -> Dict:
        """
        获取指标详情
        
        Args:
            indicator_id: str - 指标ID
            
        Returns:
            Dict: 指标详情
        """
        pass
    
    @abstractmethod
    def get_indicator_data(self, indicator_id: str, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        获取指标数据表格
        
        Args:
            indicator_id: str - 指标ID
            symbol: str - 股票代码
            days: int - 天数
            
        Returns:
            pd.DataFrame: 指标数据表格
        """
        pass
    
    @abstractmethod
    def get_data_from_adapter(self, adapter_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """
        从指定适配器获取数据（统一适配器调用入口）
        
        Args:
            adapter_type: str - 适配器类型 (akshare, tdx, baostock, tushare等)
            method: str - 调用方法名
            **kwargs: 方法参数
            
        Returns:
            Union[Dict, List[Dict], pd.DataFrame]: 适配器返回的数据
        """
        pass
    
    @abstractmethod
    def get_data_with_failover(self, data_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """
        使用故障转移机制获取数据
        
        Args:
            data_type: str - 数据类型 (realtime_quote, daily_kline等)
            method: str - 调用方法名
            **kwargs: 方法参数
            
        Returns:
            Union[Dict, List[Dict], pd.DataFrame]: 适配器返回的数据
        """
        pass
    
    # 新增的方法定义
    
    @abstractmethod
    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取分钟K线数据
        
        Args:
            symbol: str - 股票代码
            period: str - 周期 (1m/5m/15m/30m/60m)
            start_date: str - 开始日期
            end_date: str - 结束日期
            
        Returns:
            pd.DataFrame: 分钟K线数据
        """
        pass
    
    @abstractmethod
    def get_industry_classify(self) -> pd.DataFrame:
        """
        获取行业分类数据
        
        Returns:
            pd.DataFrame: 行业分类数据
        """
        pass
    
    @abstractmethod
    def get_concept_classify(self) -> pd.DataFrame:
        """
        获取概念分类数据
        
        Returns:
            pd.DataFrame: 概念分类数据
        """
        pass
    
    @abstractmethod
    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """
        获取个股的行业和概念分类信息
        
        Args:
            symbol: str - 股票代码
            
        Returns:
            Dict: 个股行业和概念信息
        """
        pass