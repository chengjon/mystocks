"""
Efinance Data Source Adapter Tests

测试efinance数据源适配器的各项功能，包括：
- 股票数据获取（K线、实时行情、龙虎榜、业绩数据、资金流向）
- 基金数据获取（净值、持仓信息、基本信息）
- 债券数据获取（实时行情、基本信息、K线数据）
- 期货数据获取（基本信息、历史行情、实时行情）
- 缓存和熔断器功能
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.adapters.efinance_adapter import EfinanceDataSource


class TestEfinanceDataSource:
    """Efinance数据源适配器测试"""

    @pytest.fixture
    def adapter(self):
        """创建测试适配器实例（禁用优化组件以便测试）"""
        return EfinanceDataSource(
            use_smart_cache=False,
            use_circuit_breaker=False,
            use_quality_validator=False,
            enable_column_mapping=True
        )

    @pytest.fixture
    def sample_stock_data(self):
        """示例股票K线数据"""
        return pd.DataFrame({
            '股票名称': ['贵州茅台', '贵州茅台'],
            '股票代码': ['600519', '600519'],
            '日期': ['2024-01-01', '2024-01-02'],
            '开盘': [1800.0, 1820.0],
            '收盘': [1820.0, 1840.0],
            '最高': [1830.0, 1850.0],
            '最低': [1790.0, 1810.0],
            '成交量': [1000, 1200],
            '成交额': [1.8e6, 2.2e6],
            '振幅': [2.22, 2.20],
            '涨跌幅': [1.11, 1.10],
            '涨跌额': [20.0, 20.0],
            '换手率': [0.5, 0.6]
        })

    @pytest.fixture
    def sample_realtime_data(self):
        """示例实时行情数据"""
        return pd.DataFrame({
            '股票代码': ['600519', '000001'],
            '股票名称': ['贵州茅台', '平安银行'],
            '涨跌幅': [1.5, -0.8],
            '最新价': [1850.0, 12.5],
            '成交量': [50000, 80000],
            '成交额': [9.2e7, 1.0e6],
            '最高': [1860.0, 12.6],
            '最低': [1830.0, 12.3],
            '今开': [1840.0, 12.4],
            '昨收': [1822.0, 12.6],
            '换手率': [2.5, 1.8]
        })

    def test_initialization(self):
        """测试适配器初始化"""
        adapter = EfinanceDataSource()
        assert adapter is not None
        assert hasattr(adapter, 'smart_cache')
        assert hasattr(adapter, 'circuit_breaker')
        assert hasattr(adapter, 'quality_validator')

    def test_initialization_with_options(self):
        """测试带选项的初始化"""
        adapter = EfinanceDataSource(
            use_smart_cache=False,
            use_circuit_breaker=False,
            use_quality_validator=False
        )
        assert adapter.smart_cache is None
        assert adapter.circuit_breaker is None
        assert adapter.quality_validator is None

    @patch('efinance.stock.get_quote_history')
    def test_get_stock_daily_success(self, mock_get_quote_history, adapter, sample_stock_data):
        """测试获取股票日线数据成功"""
        mock_get_quote_history.return_value = sample_stock_data

        result = adapter.get_stock_daily('600519', '2024-01-01', '2024-01-02')

        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'open' in result.columns
        assert 'close' in result.columns

        # 验证efinance API调用
        mock_get_quote_history.assert_called_once_with('600519', klt=101)

    @patch('efinance.stock.get_quote_history')
    def test_get_stock_daily_empty_data(self, mock_get_quote_history, adapter):
        """测试获取股票日线数据为空"""
        mock_get_quote_history.return_value = pd.DataFrame()

        result = adapter.get_stock_daily('600519', '2024-01-01', '2024-01-02')

        assert result.empty

    @patch('efinance.stock.get_realtime_quotes')
    def test_get_realtime_quotes_success(self, mock_get_realtime_quotes, adapter, sample_realtime_data):
        """测试获取实时行情成功"""
        mock_get_realtime_quotes.return_value = sample_realtime_data

        result = adapter.get_real_time_data('')

        assert not result.empty
        assert len(result) == 2
        assert '股票代码' in result.columns

    @patch('efinance.stock.get_daily_billboard')
    def test_get_dragon_tiger_list_success(self, mock_get_daily_billboard, adapter):
        """测试获取龙虎榜数据成功"""
        mock_data = pd.DataFrame({
            '股票代码': ['600519'],
            '股票名称': ['贵州茅台'],
            '上榜日期': ['2024-01-01'],
            '龙虎榜净买额': [1e7],
            '解读': ['主力买入']
        })
        mock_get_daily_billboard.return_value = mock_data

        result = adapter.get_dragon_tiger_list('2024-01-01', '2024-01-01')

        assert not result.empty
        assert 'symbol' in result.columns
        assert 'net_buy_amount' in result.columns

    @patch('efinance.stock.get_all_company_performance')
    def test_get_financial_data_success(self, mock_get_performance, adapter):
        """测试获取财务数据成功"""
        mock_data = pd.DataFrame({
            '股票代码': ['600519'],
            '营业收入': [1e9],
            '净利润': [2e8],
            '每股收益': [15.0]
        })
        mock_get_performance.return_value = mock_data

        result = adapter.get_financial_data('600519', 'annual')

        assert not result.empty
        assert 'revenue' in result.columns
        assert 'net_profit' in result.columns

    @patch('efinance.stock.get_history_bill')
    def test_get_fund_flow_data_success(self, mock_get_history_bill, adapter):
        """测试获取历史资金流向成功"""
        mock_data = pd.DataFrame({
            '主力净流入': [1e6],
            '小单净流入': [-5e5],
            '中单净流入': [2e5],
            '大单净流入': [8e5],
            '超大单净流入': [2e5]
        })
        mock_get_history_bill.return_value = mock_data

        result = adapter.get_fund_flow_data('600519')

        assert not result.empty
        assert 'main_force_net_inflow' in result.columns
        assert 'small_order_net_inflow' in result.columns

    @patch('efinance.fund.get_quote_history')
    def test_get_fund_history_success(self, mock_get_fund_history, adapter):
        """测试获取基金历史净值成功"""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '单位净值': [1.5],
            '累计净值': [2.0],
            '涨跌幅': [1.5]
        })
        mock_get_fund_history.return_value = mock_data

        result = adapter.get_fund_history('161725')

        assert not result.empty
        assert 'unit_nav' in result.columns
        assert 'cumulative_nav' in result.columns

    @patch('efinance.fund.get_invest_position')
    def test_get_fund_holdings_success(self, mock_get_holdings, adapter):
        """测试获取基金持仓信息成功"""
        mock_data = pd.DataFrame({
            '股票代码': ['600519'],
            '股票简称': ['贵州茅台'],
            '持仓占比': [10.5],
            '较上期变化': [0.5]
        })
        mock_get_holdings.return_value = mock_data

        result = adapter.get_fund_holdings('161725')

        assert not result.empty
        assert 'stock_code' in result.columns
        assert 'holding_ratio' in result.columns

    @patch('efinance.bond.get_realtime_quotes')
    def test_get_bond_realtime_quotes_success(self, mock_get_bond_quotes, adapter):
        """测试获取可转债实时行情成功"""
        mock_data = pd.DataFrame({
            '债券代码': ['123111'],
            '债券名称': ['东财转3'],
            '涨跌幅': [2.5],
            '最新价': [150.0]
        })
        mock_get_bond_quotes.return_value = mock_data

        result = adapter.get_bond_realtime_quotes()

        assert not result.empty
        assert 'bond_code' in result.columns
        assert 'bond_name' in result.columns

    @patch('efinance.futures.get_futures_base_info')
    def test_get_futures_basic_info_success(self, mock_get_futures_info, adapter):
        """测试获取期货基本信息成功"""
        mock_data = pd.DataFrame({
            '期货代码': ['ZCM'],
            '期货名称': ['动力煤主力'],
            '市场类型': ['郑商所']
        })
        mock_get_futures_info.return_value = mock_data

        result = adapter.get_futures_basic_info()

        assert not result.empty
        assert 'futures_code' in result.columns
        assert 'futures_name' in result.columns

    def test_get_stock_basic_info(self, adapter):
        """测试获取股票基本信息"""
        result = adapter.get_stock_basic('600519')

        assert isinstance(result, dict)
        assert 'symbol' in result
        assert result['symbol'] == '600519'
        assert 'source' in result
        assert result['source'] == 'efinance'

    def test_get_index_components_not_available(self, adapter):
        """测试指数成分股不可用（efinance不支持）"""
        result = adapter.get_index_components('000001')

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_news_data_not_available(self, adapter):
        """测试新闻数据不可用（efinance不支持）"""
        result = adapter.get_news_data()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_market_calendar_basic(self, adapter):
        """测试获取交易日历（基本实现）"""
        result = adapter.get_market_calendar('2024-01-01', '2024-01-05')

        assert not result.empty
        assert 'date' in result.columns
        assert 'is_trading_day' in result.columns
        assert result['is_trading_day'].all()  # 假设都是交易日

    def test_cache_stats_without_cache(self, adapter):
        """测试获取缓存统计（未启用缓存）"""
        stats = adapter.get_cache_stats()
        assert stats == {}

    def test_circuit_breaker_stats_without_circuit_breaker(self, adapter):
        """测试获取熔断器统计（未启用熔断器）"""
        stats = adapter.get_circuit_breaker_stats()
        assert stats == {}

    def test_clear_cache_without_cache(self, adapter):
        """测试清空缓存（未启用缓存）"""
        # 不应该抛出异常
        adapter.clear_cache()

    def test_reset_circuit_breaker_without_circuit_breaker(self, adapter):
        """测试重置熔断器（未启用熔断器）"""
        # 不应该抛出异常
        adapter.reset_circuit_breaker()

    def test_get_index_daily_delegates_to_stock_daily(self, adapter):
        """测试指数日线数据委托给股票日线方法"""
        with patch.object(adapter, 'get_stock_daily') as mock_get_stock_daily:
            mock_get_stock_daily.return_value = pd.DataFrame({'test': [1]})

            result = adapter.get_index_daily('000001', '2024-01-01', '2024-01-02')

            mock_get_stock_daily.assert_called_once_with('000001', '2024-01-01', '2024-01-02')
            assert result.equals(pd.DataFrame({'test': [1]}))

    def test_column_mapping_enabled(self, adapter):
        """测试列名映射启用"""
        assert adapter.enable_column_mapping is True
        assert adapter.column_mapper is not None

    def test_get_cache_key_generation(self, adapter):
        """测试缓存键生成"""
        key = adapter._get_cache_key('test_method', param1='value1', param2=123)

        expected_parts = ['test_method', 'param1:value1', 'param2:123']
        for part in expected_parts:
            assert part in key

    def test_apply_column_mapping_with_mapping(self, adapter):
        """测试应用列名映射"""
        df = pd.DataFrame({'old_col': [1, 2, 3]})
        mapping = {'old_col': 'new_col'}

        # Mock column mapper
        adapter.column_mapper.map_columns = Mock(return_value=pd.DataFrame({'new_col': [1, 2, 3]}))

        result = adapter._apply_column_mapping(df, 'test_type')

        adapter.column_mapper.map_columns.assert_called_once_with(df, "test_type")
        assert "new_col" in result.columns
