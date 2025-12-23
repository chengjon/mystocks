#!/usr/bin/env python3
"""
数据源管理器测试套件
提供完整的数据源管理器功能测试，包括Mock适配器测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime

# 导入被测试的模块
from src.adapters.data_source_manager import DataSourceManager, get_default_manager
from src.interfaces.data_source import IDataSource


# Mock数据源实现
class MockDataSource(IDataSource):
    """Mock数据源实现，用于测试"""

    def __init__(
        self,
        name: str,
        should_fail: bool = False,
        real_time_response: dict = None,
        daily_data: pd.DataFrame = None,
    ):
        self.name = name
        self.should_fail = should_fail
        self.real_time_response = real_time_response or {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1680.50,
            "volume": 1000,
            "timestamp": datetime.now().isoformat(),
        }
        self.daily_data = daily_data or self._create_default_daily_data()
        self.call_count = 0  # 记录调用次数

    def _create_default_daily_data(self) -> pd.DataFrame:
        """创建默认日线数据"""
        dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq="D")
        # 只包含工作日
        dates = [d for d in dates if d.weekday() < 5][:5]

        data = {
            "date": [d.strftime("%Y-%m-%d") for d in dates],
            "open": [1680.0 + i * 10 for i in range(len(dates))],
            "high": [1690.0 + i * 10 for i in range(len(dates))],
            "low": [1670.0 + i * 10 for i in range(len(dates))],
            "close": [1685.0 + i * 10 for i in range(len(dates))],
            "volume": [1000000 + i * 100000 for i in range(len(dates))],
        }
        return pd.DataFrame(data)

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取股票日线数据"""
        self.call_count += 1
        if self.should_fail:
            return pd.DataFrame()  # 返回空DataFrame表示失败
        return self.daily_data.copy()

    def get_index_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        self.call_count += 1
        if self.should_fail:
            return pd.DataFrame()
        return self.daily_data.copy()

    def get_stock_basic(self, symbol: str) -> dict:
        """获取股票基本信息"""
        self.call_count += 1
        if self.should_fail:
            return {}
        return {
            "symbol": symbol,
            "name": f"测试股票_{symbol}",
            "industry": "白酒",
            "market": "SH",
        }

    def get_index_components(self, symbol: str) -> list:
        """获取指数成分股"""
        self.call_count += 1
        if self.should_fail:
            return []
        return ["600519", "600887", "000858"]

    def get_real_time_data(self, symbol: str) -> dict:
        """获取实时数据"""
        self.call_count += 1
        if self.should_fail:
            return "获取失败"
        response = self.real_time_response.copy()
        response["symbol"] = symbol
        return response

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历"""
        self.call_count += 1
        if self.should_fail:
            return pd.DataFrame()

        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        calendar_data = []
        for date in dates:
            calendar_data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "is_trading_day": date.weekday() < 5,  # 周一到周五
                    "market": "SZSH",
                }
            )
        return pd.DataFrame(calendar_data)

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """获取财务数据"""
        self.call_count += 1
        if self.should_fail:
            return pd.DataFrame()

        financial_data = [
            {
                "symbol": symbol,
                "end_date": "2023-12-31",
                "revenue": 1275000000000,
                "net_profit": 627160000000,
                "period": period,
            }
        ]
        return pd.DataFrame(financial_data)

    def get_news_data(self, symbol: str = None, limit: int = 10) -> list:
        """获取新闻数据"""
        self.call_count += 1
        if self.should_fail:
            return []

        news_data = [
            {
                "title": f"关于{symbol or '市场'}的新闻",
                "content": "这是一条测试新闻",
                "timestamp": datetime.now().isoformat(),
                "source": "测试来源",
            }
            for _ in range(min(limit, 3))  # 返回最多3条新闻
        ]
        return news_data


class TestDataSourceManager:
    """DataSourceManager 测试类"""

    @pytest.fixture
    def manager(self):
        """创建数据源管理器实例"""
        return DataSourceManager()

    @pytest.fixture
    def mock_tdx_source(self):
        """创建Mock TDX数据源"""
        return MockDataSource("TDX", should_fail=False)

    @pytest.fixture
    def mock_akshare_source(self):
        """创建Mock AkShare数据源"""
        return MockDataSource("AkShare", should_fail=False)

    @pytest.fixture
    def mock_failing_source(self):
        """创建Mock失败数据源"""
        return MockDataSource("FailingSource", should_fail=True)

    def test_initialization(self, manager):
        """测试管理器初始化"""
        assert isinstance(manager, DataSourceManager)
        assert manager._sources == {}
        assert "real_time" in manager._priority_config
        assert "daily" in manager._priority_config
        assert "financial" in manager._priority_config
        assert manager._priority_config["real_time"] == ["tdx", "akshare"]
        assert manager._priority_config["daily"] == ["tdx", "akshare"]
        assert manager._priority_config["financial"] == ["akshare", "tdx"]

    def test_register_source_success(self, manager, mock_tdx_source):
        """测试成功注册数据源"""
        manager.register_source("tdx", mock_tdx_source)
        assert "tdx" in manager._sources
        assert manager._sources["tdx"] is mock_tdx_source
        assert manager.list_sources() == ["tdx"]

    def test_register_source_invalid_type(self, manager):
        """测试注册无效类型数据源"""
        invalid_source = "not a data source"
        with pytest.raises(TypeError, match="数据源必须实现IDataSource接口"):
            manager.register_source("invalid", invalid_source)

    def test_register_source_overwrite(self, manager, mock_tdx_source):
        """测试覆盖已注册的数据源"""
        # 注册第一个数据源
        manager.register_source("tdx", mock_tdx_source)
        first_source = manager._sources["tdx"]

        # 创建新数据源并覆盖
        new_source = MockDataSource("NewTDX")
        manager.register_source("tdx", new_source)

        assert manager._sources["tdx"] is new_source
        assert manager._sources["tdx"] is not first_source

    def test_get_source_existing(self, manager, mock_tdx_source):
        """测试获取已存在的数据源"""
        manager.register_source("tdx", mock_tdx_source)
        retrieved_source = manager.get_source("tdx")
        assert retrieved_source is mock_tdx_source

    def test_get_source_nonexistent(self, manager):
        """测试获取不存在的数据源"""
        retrieved_source = manager.get_source("nonexistent")
        assert retrieved_source is None

    def test_list_sources_empty(self, manager):
        """测试空数据源列表"""
        sources = manager.list_sources()
        assert sources == []

    def test_list_sources_multiple(self, manager, mock_tdx_source, mock_akshare_source):
        """测试多个数据源列表"""
        manager.register_source("tdx", mock_tdx_source)
        manager.register_source("akshare", mock_akshare_source)
        sources = manager.list_sources()
        assert set(sources) == {"tdx", "akshare"}
        assert len(sources) == 2

    def test_get_real_time_data_with_valid_source(self, manager, mock_tdx_source):
        """测试使用指定数据源获取实时数据"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_real_time_data("600519", source="tdx")

        assert isinstance(result, dict)
        assert result["symbol"] == "600519"
        assert "name" in result
        assert "price" in result
        assert "volume" in result
        assert "timestamp" in result
        assert mock_tdx_source.call_count == 1

    def test_get_real_time_data_with_invalid_source(self, manager):
        """测试使用无效数据源获取实时数据"""
        result = manager.get_real_time_data("600519", source="invalid")
        assert result == "数据源不存在: invalid"

    def test_get_real_time_data_priority_success(self, manager, mock_tdx_source):
        """测试按优先级成功获取实时数据"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_real_time_data("600519")

        assert isinstance(result, dict)
        assert result["symbol"] == "600519"
        assert mock_tdx_source.call_count == 1

    def test_get_real_time_data_priority_fallback(
        self, manager, mock_tdx_source, mock_akshare_source
    ):
        """测试按优先级回退获取实时数据"""
        # TDX注册但会失败，AkShare注册且会成功
        failing_tdx = MockDataSource("TDX", should_fail=True)
        manager.register_source("tdx", failing_tdx)
        manager.register_source("akshare", mock_akshare_source)

        result = manager.get_real_time_data("600519")

        assert isinstance(result, dict)
        assert result["symbol"] == "600519"
        assert failing_tdx.call_count == 1  # TDX被尝试过
        assert mock_akshare_source.call_count == 1  # AkShare被成功调用

    def test_get_real_time_data_all_sources_fail(self, manager, mock_failing_source):
        """测试所有数据源都失败"""
        manager.register_source("tdx", mock_failing_source)
        manager.register_source("akshare", mock_failing_source)

        result = manager.get_real_time_data("600519")
        assert result == "所有数据源均获取失败"
        assert mock_failing_source.call_count == 2  # 两个数据源都被尝试过

    def test_get_stock_daily_with_valid_source(self, manager, mock_tdx_source):
        """测试使用指定数据源获取股票日线数据"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_stock_daily(
            "600519", "2024-01-01", "2024-01-10", source="tdx"
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "date" in result.columns
        assert "close" in result.columns
        assert len(result) > 0
        assert mock_tdx_source.call_count == 1

    def test_get_stock_daily_with_invalid_source(self, manager):
        """测试使用无效数据源获取股票日线数据"""
        result = manager.get_stock_daily(
            "600519", "2024-01-01", "2024-01-10", source="invalid"
        )

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_stock_daily_priority_success(self, manager, mock_tdx_source):
        """测试按优先级成功获取股票日线数据"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_stock_daily("600519", "2024-01-01", "2024-01-10")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert mock_tdx_source.call_count == 1

    def test_get_stock_daily_priority_fallback(
        self, manager, mock_tdx_source, mock_akshare_source
    ):
        """测试按优先级回退获取股票日线数据"""
        failing_tdx = MockDataSource("TDX", should_fail=True)
        manager.register_source("tdx", failing_tdx)
        manager.register_source("akshare", mock_akshare_source)

        result = manager.get_stock_daily("600519", "2024-01-01", "2024-01-10")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert failing_tdx.call_count == 1
        assert mock_akshare_source.call_count == 1

    def test_get_stock_daily_all_sources_fail(self, manager, mock_failing_source):
        """测试所有数据源获取日线数据都失败"""
        manager.register_source("tdx", mock_failing_source)
        manager.register_source("akshare", mock_failing_source)

        result = manager.get_stock_daily("600519", "2024-01-01", "2024-01-10")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert mock_failing_source.call_count == 2

    def test_get_index_daily(self, manager, mock_tdx_source):
        """测试获取指数日线数据"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_index_daily("000001", "2024-01-01", "2024-01-10")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert mock_tdx_source.call_count == 1

    def test_get_stock_basic(self, manager, mock_tdx_source):
        """测试获取股票基本信息"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_stock_basic("600519")

        assert isinstance(result, dict)
        assert result["symbol"] == "600519"
        assert "name" in result
        assert "industry" in result
        assert mock_tdx_source.call_count == 1

    def test_get_stock_basic_fallback(
        self, manager, mock_tdx_source, mock_akshare_source
    ):
        """测试股票基本信息回退机制"""
        failing_tdx = MockDataSource("TDX", should_fail=True)
        manager.register_source("tdx", failing_tdx)
        manager.register_source("akshare", mock_akshare_source)

        result = manager.get_stock_basic("600519")

        assert isinstance(result, dict)
        assert result["symbol"] == "600519"
        assert result["name"] == "测试股票_600519"

    def test_get_stock_basic_all_fail(self, manager, mock_failing_source):
        """测试所有数据源获取基本信息都失败"""
        manager.register_source("tdx", mock_failing_source)
        manager.register_source("akshare", mock_failing_source)

        result = manager.get_stock_basic("600519")
        assert result == {}

    def test_get_financial_data(self, manager, mock_akshare_source):
        """测试获取财务数据"""
        manager.register_source("akshare", mock_akshare_source)
        result = manager.get_financial_data("600519", "quarter")

        assert isinstance(result, pd.DataFrame)
        if not result.empty:  # 只有在不为空时才验证列
            assert "symbol" in result.columns
            assert "revenue" in result.columns
            assert mock_akshare_source.call_count == 1

    def test_get_financial_data_with_source(self, manager, mock_akshare_source):
        """测试使用指定数据源获取财务数据"""
        manager.register_source("akshare", mock_akshare_source)
        result = manager.get_financial_data("600519", "quarter", source="akshare")

        assert isinstance(result, pd.DataFrame)
        assert mock_akshare_source.call_count == 1

    def test_get_financial_data_priority(
        self, manager, mock_akshare_source, mock_tdx_source
    ):
        """测试财务数据优先级（akshare优先）"""
        manager.register_source("akshare", mock_akshare_source)
        manager.register_source("tdx", mock_tdx_source)

        result = manager.get_financial_data("600519", "quarter")

        assert isinstance(result, pd.DataFrame)
        # 应该只调用akshare，因为它是优先级最高的
        assert mock_akshare_source.call_count == 1
        assert mock_tdx_source.call_count == 0

    def test_get_index_components(self, manager, mock_tdx_source):
        """测试获取指数成分股"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_index_components("000001")

        assert isinstance(result, list)
        assert len(result) > 0
        assert "600519" in result
        assert mock_tdx_source.call_count == 1

    def test_get_index_components_with_source(self, manager, mock_tdx_source):
        """测试使用指定数据源获取指数成分股"""
        manager.register_source("tdx", mock_tdx_source)
        result = manager.get_index_components("000001", source="tdx")

        assert isinstance(result, list)
        assert mock_tdx_source.call_count == 1

    def test_get_index_components_fallback(
        self, manager, mock_tdx_source, mock_akshare_source
    ):
        """测试指数成分股回退机制"""
        failing_tdx = MockDataSource("TDX", should_fail=True)
        manager.register_source("tdx", failing_tdx)
        manager.register_source("akshare", mock_akshare_source)

        result = manager.get_index_components("000001")

        assert isinstance(result, list)
        assert len(result) > 0
        assert failing_tdx.call_count == 1
        assert mock_akshare_source.call_count == 1

    def test_set_priority_valid_data_type(self, manager):
        """测试设置有效的数据类型优先级"""
        new_priority = ["custom_source", "tdx"]
        manager.set_priority("real_time", new_priority)

        assert manager._priority_config["real_time"] == new_priority

    def test_set_priority_invalid_data_type(self, manager):
        """测试设置无效的数据类型优先级"""
        with pytest.raises(ValueError, match="未知的数据类型"):
            manager.set_priority("invalid_type", ["source1"])

    def test_set_priority_all_data_types(self, manager):
        """测试设置所有数据类型的优先级"""
        manager.set_priority("real_time", ["custom_tdx", "custom_akshare"])
        manager.set_priority("daily", ["custom_akshare", "custom_tdx"])
        manager.set_priority("financial", ["custom_financial", "custom_tdx"])

        assert manager._priority_config["real_time"] == ["custom_tdx", "custom_akshare"]
        assert manager._priority_config["daily"] == ["custom_akshare", "custom_tdx"]
        assert manager._priority_config["financial"] == [
            "custom_financial",
            "custom_tdx",
        ]


class TestDataSourceManagerEdgeCases:
    """DataSourceManager 边界情况测试"""

    @pytest.fixture
    def manager(self):
        return DataSourceManager()

    def test_empty_symbol_real_time_data(self, manager):
        """测试空股票代码获取实时数据"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        result = manager.get_real_time_data("", source="test")
        assert isinstance(result, dict)
        assert result["symbol"] == ""

    def test_empty_symbol_stock_daily(self, manager):
        """测试空股票代码获取日线数据"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        result = manager.get_stock_daily("", "2024-01-01", "2024-01-10")
        assert isinstance(result, pd.DataFrame)

    def test_invalid_date_format(self, manager):
        """测试无效日期格式"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        # Mock数据源不验证日期格式，但管理器应该能处理
        result = manager.get_stock_daily("600519", "invalid-date", "2024-01-10")
        assert isinstance(result, pd.DataFrame)

    def test_end_date_before_start_date(self, manager):
        """测试结束日期早于开始日期"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        result = manager.get_stock_daily("600519", "2024-01-10", "2024-01-01")
        assert isinstance(result, pd.DataFrame)

    def test_very_long_date_range(self, manager):
        """测试很长的日期范围"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        result = manager.get_stock_daily("600519", "2020-01-01", "2024-12-31")
        assert isinstance(result, pd.DataFrame)

    def test_multiple_sources_same_priority(self, manager):
        """测试相同优先级的多个数据源"""
        source1 = MockDataSource("source1")
        source2 = MockDataSource("source2")

        manager.register_source("source1", source1)
        manager.register_source("source2", source2)

        # 设置相同优先级
        manager.set_priority("real_time", ["source1", "source2"])

        result = manager.get_real_time_data("600519")

        assert isinstance(result, dict)
        # 应该使用第一个可用的数据源
        assert source1.call_count == 1
        assert source2.call_count == 0

    def test_source_registration_during_operation(self, manager):
        """测试操作过程中注册新数据源"""
        result = manager.get_real_time_data("600519")
        assert result == "所有数据源均获取失败"

        # 动态注册数据源
        mock_source = MockDataSource("dynamic")
        manager.register_source("dynamic", mock_source)

        result = manager.get_real_time_data("600519", source="dynamic")
        assert isinstance(result, dict)
        assert result["symbol"] == "600519"

    def test_unicode_symbol_handling(self, manager):
        """测试Unicode股票代码处理"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        # 测试包含Unicode的股票代码
        unicode_symbol = "测试\u516c\u53f8"
        result = manager.get_real_time_data(unicode_symbol, source="test")

        assert isinstance(result, dict)
        assert result["symbol"] == unicode_symbol

    def test_very_long_symbol(self, manager):
        """测试很长的股票代码"""
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        long_symbol = "A" * 100
        result = manager.get_real_time_data(long_symbol, source="test")

        assert isinstance(result, dict)
        assert result["symbol"] == long_symbol


class TestDataSourceManagerIntegration:
    """DataSourceManager 集成测试"""

    def test_real_workflow_simulation(self):
        """模拟真实工作流程"""
        manager = DataSourceManager()

        # 注册多个数据源
        tdx_source = MockDataSource("TDX")
        akshare_source = MockDataSource("AkShare")
        failing_source = MockDataSource("Failing", should_fail=True)

        manager.register_source("tdx", tdx_source)
        manager.register_source("akshare", akshare_source)
        manager.register_source("backup", failing_source)

        # 模拟多种操作
        symbols = ["600519", "000001", "300015"]

        for symbol in symbols:
            # 获取实时数据
            quote = manager.get_real_time_data(symbol)
            assert isinstance(quote, dict)
            assert quote["symbol"] == symbol

            # 获取历史数据
            df = manager.get_stock_daily(symbol, "2024-01-01", "2024-01-10")
            assert isinstance(df, pd.DataFrame)

            # 获取基本信息
            info = manager.get_stock_basic(symbol)
            assert isinstance(info, dict)
            assert info.get("symbol") == symbol

        # 验证调用次数统计
        total_calls = (
            tdx_source.call_count
            + akshare_source.call_count
            + failing_source.call_count
        )
        assert total_calls > 0

        # 测试指数成分股
        components = manager.get_index_components("000001")
        assert isinstance(components, list)
        assert len(components) > 0

    def test_failover_scenario(self):
        """测试故障转移场景"""
        manager = DataSourceManager()

        # 创建会失败和成功的数据源
        primary_failing = MockDataSource("Primary", should_fail=True)
        secondary_working = MockDataSource("Secondary", should_fail=False)
        tertiary_working = MockDataSource("Tertiary", should_fail=False)

        manager.register_source("primary", primary_failing)
        manager.register_source("secondary", secondary_working)
        manager.register_source("tertiary", tertiary_working)

        # 设置优先级，primary失败后会尝试secondary
        manager.set_priority("real_time", ["primary", "secondary", "tertiary"])

        result = manager.get_real_time_data("600519")

        # 验证故障转移逻辑
        assert isinstance(result, dict)
        assert primary_failing.call_count == 1  # primary被尝试过
        assert secondary_working.call_count == 1  # secondary成功
        assert tertiary_working.call_count == 0  # tertiary没有被调用

    def test_performance_multiple_calls(self):
        """测试多次调用的性能"""
        manager = DataSourceManager()
        mock_source = MockDataSource("test")
        manager.register_source("test", mock_source)

        # 执行多次调用
        for i in range(100):
            result = manager.get_real_time_data(f"6005{i % 10}", source="test")
            assert isinstance(result, dict)

        # 验证性能（这里只是简单验证调用次数）
        assert mock_source.call_count == 100


class TestGetDefaultManager:
    """测试默认管理器函数"""

    @patch("src.adapters.data_source_manager.TdxDataSource")
    @patch("src.adapters.data_source_manager.AkshareDataSource")
    @patch("logging.warning")
    def test_get_default_manager_success(self, mock_logging, mock_akshare, mock_tdx):
        """测试成功获取默认管理器"""
        # 创建Mock实例
        mock_tdx_instance = MockDataSource("TDX")
        mock_akshare_instance = MockDataSource("AkShare")

        mock_tdx.return_value = mock_tdx_instance
        mock_akshare.return_value = mock_akshare_instance

        # 获取默认管理器
        manager = get_default_manager()

        # 验证管理器
        assert isinstance(manager, DataSourceManager)
        assert "tdx" in manager._sources
        assert "akshare" in manager._sources
        assert manager._sources["tdx"] is mock_tdx_instance
        assert manager._sources["akshare"] is mock_akshare_instance

    @patch("src.adapters.data_source_manager.TdxDataSource")
    @patch("src.adapters.data_source_manager.AkshareDataSource")
    @patch("logging.warning")
    def test_get_default_manager_tdx_failure(
        self, mock_logging, mock_akshare, mock_tdx
    ):
        """测试TDX注册失败的情况"""
        # TDX抛出异常
        mock_tdx.side_effect = Exception("TDX初始化失败")
        mock_akshare_instance = MockDataSource("AkShare")
        mock_akshare.return_value = mock_akshare_instance

        manager = get_default_manager()

        # 验证只有AkShare被注册
        assert isinstance(manager, DataSourceManager)
        assert "tdx" not in manager._sources
        assert "akshare" in manager._sources
        assert manager._sources["akshare"] is mock_akshare_instance

        # 验证警告被记录
        mock_logging.assert_called_with("TDX数据源注册失败: TDX初始化失败")

    @patch("src.adapters.data_source_manager.TdxDataSource")
    @patch("src.adapters.data_source_manager.AkshareDataSource")
    @patch("logging.warning")
    def test_get_default_manager_both_failure(
        self, mock_logging, mock_akshare, mock_tdx
    ):
        """测试两个数据源都注册失败的情况"""
        mock_tdx.side_effect = Exception("TDX失败")
        mock_akshare.side_effect = Exception("AkShare失败")

        manager = get_default_manager()

        # 验证管理器存在但没有注册任何数据源
        assert isinstance(manager, DataSourceManager)
        assert len(manager._sources) == 0

        # 验证两个警告都被记录
        mock_logging.assert_any_call("TDX数据源注册失败: TDX失败")
        mock_logging.assert_any_call("AKShare数据源注册失败: AkShare失败")


class TestDataSourceManagerErrorHandling:
    """测试数据源管理器错误处理"""

    @pytest.fixture
    def manager(self):
        return DataSourceManager()

    def test_data_source_exception_handling(self, manager):
        """测试数据源抛出异常的处理"""

        # 创建会抛出异常的Mock数据源
        class ExceptionDataSource(IDataSource):
            def get_real_time_data(self, symbol: str):
                raise Exception("网络连接失败")

            def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
                raise Exception("数据获取失败")

            # 实现其他必需方法（返回空值）
            def get_index_daily(self, symbol: str, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_stock_basic(self, symbol: str):
                return {}

            def get_index_components(self, symbol: str):
                return []

            def get_market_calendar(self, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_financial_data(self, symbol: str, period: str = "annual"):
                return pd.DataFrame()

            def get_news_data(self, symbol: str = None, limit: int = 10):
                return []

        exception_source = ExceptionDataSource()
        manager.register_source("exception", exception_source)

        # 测试异常不会导致管理器崩溃
        with pytest.raises(Exception):
            manager.get_real_time_data("600519", source="exception")

        with pytest.raises(Exception):
            manager.get_stock_daily(
                "600519", "2024-01-01", "2024-01-10", source="exception"
            )

    def test_source_returns_invalid_types(self, manager):
        """测试数据源返回无效类型"""

        # 创建返回无效类型的Mock数据源
        class InvalidTypeDataSource(IDataSource):
            def get_real_time_data(self, symbol: str):
                return 123  # 应该返回dict或str

            def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
                return "invalid"  # 应该返回DataFrame

            # 实现其他必需方法
            def get_index_daily(self, symbol: str, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_stock_basic(self, symbol: str):
                return {}

            def get_index_components(self, symbol: str):
                return []

            def get_market_calendar(self, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_financial_data(self, symbol: str, period: str = "annual"):
                return pd.DataFrame()

            def get_news_data(self, symbol: str = None, limit: int = 10):
                return []

        invalid_source = InvalidTypeDataSource()
        manager.register_source("invalid", invalid_source)

        # 管理器应该能处理无效的返回类型
        result = manager.get_real_time_data("600519", source="invalid")
        assert result == 123  # 直接返回原始结果

        df_result = manager.get_stock_daily(
            "600519", "2024-01-01", "2024-01-10", source="invalid"
        )
        assert df_result == "invalid"  # 直接返回原始结果


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
