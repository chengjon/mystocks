#!/usr/bin/env python3
"""
BaseDataSourceAdapter 测试套件
提供完整的适配器基类功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from unittest.mock import Mock, patch

# 导入被测试的模块
from src.adapters.base_adapter import BaseDataSourceAdapter, QualityMixin


class ConcreteTestAdapter(BaseDataSourceAdapter):
    """用于测试的具体适配器实现"""

    def __init__(self, source_name: str = "test_adapter"):
        super().__init__(source_name)


class TestBaseDataSourceAdapter:
    """BaseDataSourceAdapter 测试类"""

    @pytest.fixture
    def adapter(self):
        """创建测试适配器实例"""
        return ConcreteTestAdapter("test_source")

    @pytest.fixture
    def sample_dataframe(self):
        """创建示例DataFrame数据"""
        return pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                "symbol": ["AAPL"] * 5,
                "open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "high": [101.0, 102.0, 103.0, 104.0, 105.0],
                "low": [99.0, 100.0, 101.0, 102.0, 103.0],
                "close": [101.0, 102.0, 103.0, 104.0, 105.0],
                "volume": [1000000] * 5,
            }
        )

    def test_adapter_initialization(self, adapter):
        """测试适配器初始化"""
        assert adapter.source_name == "test_source"
        assert adapter.quality_validator is not None
        assert adapter.logger is not None

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_quality_check_with_valid_data(
        self, mock_validator_class, adapter, sample_dataframe
    ):
        """测试有效数据的质量检查"""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 95.0,
            "issues": [],
        }

        adapter = ConcreteTestAdapter("test_source")
        result = adapter._apply_quality_check(sample_dataframe, "AAPL", "daily")

        assert result is not None
        assert len(result) == len(sample_dataframe)

    def test_quality_check_with_empty_dataframe(self, adapter):
        """测试空DataFrame的质量检查"""
        empty_df = pd.DataFrame()
        result = adapter._apply_quality_check(empty_df, "AAPL", "daily")
        assert result.empty

    def test_validate_symbol_valid(self, adapter):
        """测试有效股票代码验证"""
        result = adapter._validate_symbol("AAPL")
        assert result == "AAPL"
        result = adapter._validate_symbol(" aapl ")
        assert result == "AAPL"

    def test_validate_symbol_invalid(self, adapter):
        """测试无效股票代码验证"""
        with pytest.raises(ValueError, match="无效的股票代码"):
            adapter._validate_symbol("")
        with pytest.raises(ValueError, match="无效的股票代码"):
            adapter._validate_symbol(None)
        with pytest.raises(ValueError, match="股票代码长度不足"):
            adapter._validate_symbol("AA")

    def test_validate_date_range_valid(self, adapter):
        """测试有效日期范围验证"""
        start_date, end_date = adapter._validate_date_range("20240101", "20240110")
        assert start_date == "20240101"
        assert end_date == "20240110"

    def test_validate_date_range_invalid(self, adapter):
        """测试无效日期范围验证"""
        with pytest.raises(ValueError, match="开始日期不能大于结束日期"):
            adapter._validate_date_range("20240110", "20240101")

    def test_handle_empty_data(self, adapter):
        """测试处理空数据"""
        result = adapter._handle_empty_data("AAPL", "daily")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_log_data_fetch(self, adapter):
        """测试数据获取日志记录"""
        with patch.object(adapter.logger, "info"):
            adapter._log_data_fetch("AAPL", "daily", 100)


class TestQualityMixin:
    """QualityMixin 测试类"""

    def test_quality_mixin_initialization(self):
        """测试QualityMixin初始化"""

        class TestClass(QualityMixin):
            def __init__(self):
                self.source_name = "test_source"
                super().__init__()

        test_obj = TestClass()
        assert hasattr(test_obj, "quality_validator")

    def test_quality_mixin_without_source_name(self):
        """测试没有source_name的QualityMixin"""

        class TestClass(QualityMixin):
            def __init__(self):
                super().__init__()

        test_obj = TestClass()
        assert not hasattr(test_obj, "quality_validator")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
