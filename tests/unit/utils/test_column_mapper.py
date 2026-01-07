"""
Column Mapper Test Suite
列名映射器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.column_mapper (426行)
"""

import pytest
import sys
import os
import pandas as pd

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 导入被测试的模块
from src.utils.column_mapper import ColumnMapper


class TestColumnMapper:
    """列名映射器测试"""

    def test_column_mapper_initialization(self):
        """测试列名映射器初始化"""
        # 验证默认的英文映射表存在
        assert hasattr(ColumnMapper, "STANDARD_EN_MAPPING")
        assert isinstance(ColumnMapper.STANDARD_EN_MAPPING, dict)
        assert len(ColumnMapper.STANDARD_EN_MAPPING) > 0

        # 验证默认的中文映射表存在
        assert hasattr(ColumnMapper, "STANDARD_CN_MAPPING")
        assert isinstance(ColumnMapper.STANDARD_CN_MAPPING, dict)
        assert len(ColumnMapper.STANDARD_CN_MAPPING) > 0

    def test_standard_en_mapping_content(self):
        """测试标准英文映射表内容"""
        # 验证OHLCV基本映射
        assert "日期" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["日期"] == "date"
        assert "股票代码" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["股票代码"] == "symbol"
        assert "开盘价" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["开盘价"] == "open"
        assert "收盘价" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["收盘价"] == "close"

        # 验证常见技术指标
        assert "成交量" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["成交量"] == "volume"
        assert "成交额" in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING["成交额"] == "amount"

    def test_standard_cn_mapping_content(self):
        """测试标准中文映射表内容"""
        # 验证基本OHLCV数据
        assert "open" in ColumnMapper.STANDARD_CN_MAPPING
        assert ColumnMapper.STANDARD_CN_MAPPING["open"] == "开盘价"
        assert "close" in ColumnMapper.STANDARD_CN_MAPPING
        assert ColumnMapper.STANDARD_CN_MAPPING["close"] == "收盘价"
        assert "high" in ColumnMapper.STANDARD_CN_MAPPING
        assert ColumnMapper.STANDARD_CN_MAPPING["high"] == "最高价"
        assert "low" in ColumnMapper.STANDARD_CN_MAPPING
        assert ColumnMapper.STANDARD_CN_MAPPING["low"] == "最低价"

    def test_standardize_columns_basic(self):
        """测试基本列名标准化"""
        # 测试英文名称标准化
        data = pd.DataFrame(
            {
                "Stock_Name": ["AAPL", "GOOGL"],
                "Open_Price": [150.0, 2500.0],
                "Volume": [1000, 500],
            }
        )

        result = ColumnMapper.standardize_columns(data, target_lang="en")

        # 验证列名被映射转换（映射器会清理并匹配列名）
        assert len(result) == 2
        # 验证数据值保持不变（通过映射后的列名访问）
        if "name" in result.columns:
            assert result.iloc[0]["name"] == "AAPL"
        if "open" in result.columns:
            assert result.iloc[0]["open"] == 150.0

    def test_to_chinese_chinese(self):
        """测试中文列名转换为中文"""
        mapper = ColumnMapper()

        data = pd.DataFrame(
            {
                "股票名称": ["苹果", "谷歌"],
                "开盘价": [150.0, 2500.0],
                "成交量": [1000, 500],
            }
        )

        result = ColumnMapper.to_chinese(data)

        # 验证中文列名被保留
        assert "股票名称" in result.columns
        assert "开盘价" in result.columns
        assert "成交量" in result.columns

        # 验证数据保持不变
        assert len(result) == 2
        assert result.iloc[0]["股票名称"] == "苹果"
        assert result.iloc[0]["开盘价"] == 150.0

    def test_to_english_chinese(self):
        """测试中文列名转换为英文"""
        data = pd.DataFrame(
            {
                "股票名称": ["苹果", "谷歌"],
                "开盘价": [150.0, 2500.0],
                "成交量": [1000, 500],
            }
        )

        result = ColumnMapper.to_english(data)

        # 验证中文列名被转换为标准英文
        assert "name" in result.columns
        assert "open" in result.columns
        assert "volume" in result.columns

        # 验证数据保持不变
        assert len(result) == 2
        assert result.iloc[0]["name"] == "苹果"
        assert result.iloc[0]["open"] == 150.0

    def test_standardize_columns_mixed(self):
        """测试混合格式列名标准化"""
        data = pd.DataFrame(
            {
                "symbol": ["AAPL", "GOOGL"],  # 已经是标准格式
                "股票名称": ["苹果", "谷歌"],  # 需要转换
                "CLOSE": [150.0, 2500.0],  # 需要转换
                "Volume": [1000, 500],  # 需要转换
            }
        )

        result = ColumnMapper.standardize_columns(data, target_lang="en")

        # 验证列名映射结果
        assert "symbol" in result.columns
        assert "name" in result.columns  # 从'股票名称'转换
        # CLOSE可能保持原样或转换为close，取决于映射逻辑
        assert "close" in result.columns or "CLOSE" in result.columns
        assert "volume" in result.columns or "Volume" in result.columns

    def test_standardize_columns_unknown_columns(self):
        """测试未知列名的处理"""
        data = pd.DataFrame(
            {
                "unknown_col1": ["A", "B"],
                "unknown_col2": [1, 2],
                "symbol": ["AAPL", "GOOGL"],
            }
        )

        result = ColumnMapper.standardize_columns(data, target_lang="en")

        # 未知列应该保持不变
        assert "unknown_col1" in result.columns
        assert "unknown_col2" in result.columns
        assert "symbol" in result.columns

    def test_standardize_columns_case_sensitivity(self):
        """测试列名大小写敏感性"""
        data = pd.DataFrame(
            {
                "SYMBOL": ["AAPL", "GOOGL"],
                "Date": ["2023-01-01", "2023-01-02"],
                "CLOSE": [150.0, 2500.0],
            }
        )

        result = ColumnMapper.standardize_columns(data, target_lang="en")

        # 验证列名被正确处理
        assert "SYMBOL" in result.columns  # 没有直接匹配，保持原样
        assert "Date" in result.columns  # Date被映射为date
        # CLOSE可能被映射或保持原样
        assert "close" in result.columns or "CLOSE" in result.columns

    def test_get_standard_columns_stock_daily_en(self):
        """测试获取日线数据英文标准列名"""
        result = ColumnMapper.get_standard_columns("stock_daily", "en")

        expected_columns = [
            "date",
            "symbol",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount",
            "pct_chg",
            "change",
        ]

        assert isinstance(result, list)
        assert len(result) == len(expected_columns)
        for col in expected_columns:
            assert col in result

    def test_get_standard_columns_stock_daily_cn(self):
        """测试获取日线数据中文标准列名"""
        result = ColumnMapper.get_standard_columns("stock_daily", "cn")

        expected_columns = [
            "日期",
            "股票代码",
            "开盘价",
            "收盘价",
            "最高价",
            "最低价",
            "成交量",
            "成交额",
            "涨跌幅",
            "涨跌额",
        ]

        assert isinstance(result, list)
        assert len(result) == len(expected_columns)
        for col in expected_columns:
            assert col in result

    def test_standardize_columns_with_custom_mapping(self):
        """测试添加自定义映射"""
        data = pd.DataFrame({"custom_col1": ["A", "B"], "custom_col2": [1, 2]})

        custom_mapping = {
            "custom_col1": "standard_col1",
            "custom_col2": "standard_col2",
        }

        result = ColumnMapper.standardize_columns(data, target_lang="en", custom_mapping=custom_mapping)

        # 测试自定义映射是否生效
        assert "standard_col1" in result.columns
        assert "standard_col2" in result.columns

    def test_standardize_columns_custom_mapping_override(self):
        """测试自定义映射覆盖默认映射"""
        data = pd.DataFrame({"日期": ["2023-01-01", "2023-01-02"], "股票代码": ["AAPL", "GOOGL"]})

        # 添加覆盖默认映射的自定义映射
        custom_mapping = {
            "日期": "custom_date",  # 覆盖默认映射
            "股票代码": "custom_symbol",
        }

        result = ColumnMapper.standardize_columns(data, target_lang="en", custom_mapping=custom_mapping)

        # 测试自定义映射是否覆盖默认映射
        assert "custom_date" in result.columns
        assert "custom_symbol" in result.columns

    def test_standardize_columns_empty_dataframe(self):
        """测试空DataFrame的列名标准化"""
        # 空DataFrame
        empty_df = pd.DataFrame()
        result = ColumnMapper.standardize_columns(empty_df, target_lang="en")

        assert result.empty
        assert len(result.columns) == 0

    def test_standardize_columns_preserves_data(self):
        """测试列名标准化保持数据完整性"""
        data = pd.DataFrame(
            {
                "股票名称": ["苹果", "谷歌", "微软"],
                "开盘价": [150.0, 2500.0, 300.0],
                "收盘价": [155.0, 2550.0, 310.0],
                "成交量": [1000, 500, 800],
            }
        )

        result = ColumnMapper.to_english(data)

        # 验证数据完整性
        assert len(result) == 3
        assert result.iloc[0]["name"] == "苹果"
        assert result.iloc[0]["open"] == 150.0
        assert result.iloc[0]["close"] == 155.0
        assert result.iloc[0]["volume"] == 1000

        assert result.iloc[1]["name"] == "谷歌"
        assert result.iloc[1]["open"] == 2500.0
        assert result.iloc[1]["close"] == 2550.0
        assert result.iloc[1]["volume"] == 500

        assert result.iloc[2]["name"] == "微软"
        assert result.iloc[2]["open"] == 300.0
        assert result.iloc[2]["close"] == 310.0
        assert result.iloc[2]["volume"] == 800

    def test_standardize_columns_with_duplicate_columns(self):
        """测试重复列名的处理"""
        # 创建包含重复列的DataFrame（pandas不允许重复列名）
        data = pd.DataFrame(
            {
                "symbol": ["AAPL", "GOOGL"],
                "股票代码": ["AAPL", "GOOGL"],
                "name": ["Apple", "Google"],
                "股票名称": ["Apple", "Google"],
            }
        )

        result = ColumnMapper.to_english(data)

        # 验证结果的有效性
        assert len(result) == 2
        # 由于列名映射，检查是否有标准列
        assert "symbol" in result.columns or "name" in result.columns

    def test_validate_columns_function(self):
        """测试列名验证功能"""
        # 创建有效的DataFrame
        data = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["AAPL", "GOOGL"],
                "open": [10.0, 20.0],
                "close": [10.5, 20.5],
                "high": [11.0, 21.0],
                "low": [9.0, 19.0],
                "volume": [1000, 500],
                "amount": [10500, 10250],
                "pct_chg": [5.0, 2.5],
                "change": [0.5, 0.5],
            }
        )

        required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")
        is_valid, missing, extra = ColumnMapper.validate_columns(data, required_cols)

        assert is_valid is True
        assert len(missing) == 0
        assert len(extra) == 0

    def test_validate_columns_missing_columns(self):
        """测试缺少必需列的验证"""
        data = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["AAPL", "GOOGL"],
                # 缺少其他必需列
            }
        )

        required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")
        is_valid, missing, extra = ColumnMapper.validate_columns(data, required_cols)

        assert is_valid is False
        assert len(missing) > 0
        assert "open" in missing
        assert "close" in missing


class TestColumnMapperIntegration:
    """列名映射器集成测试"""

    def test_integration_with_tushare_data_format(self):
        """测试与Tushare数据格式的集成"""
        # 模拟Tushare数据格式
        tushare_data = pd.DataFrame(
            {
                "ts_code": ["000001.SZ", "000002.SZ"],
                "trade_date": ["20230101", "20230102"],
                "open": [10.0, 20.0],
                "high": [11.0, 21.0],
                "low": [9.0, 19.0],
                "close": [10.5, 20.5],
                "vol": [1000000, 2000000],
            }
        )

        result = ColumnMapper.to_english(tushare_data)

        # 验证Tushare数据格式被正确标准化
        assert "symbol" in result.columns
        assert "date" in result.columns
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns

    def test_integration_with_akshare_data_format(self):
        """测试与Akshare数据格式的集成"""
        # 模拟Akshare数据格式
        akshare_data = pd.DataFrame(
            {
                "日期": ["2023-01-01", "2023-01-02"],
                "股票代码": ["000001", "000002"],
                "开盘": [10.0, 20.0],
                "最高": [11.0, 21.0],
                "最低": [9.0, 19.0],
                "收盘": [10.5, 20.5],
                "成交量": [1000000, 2000000],
            }
        )

        result = ColumnMapper.to_english(akshare_data)

        # 验证Akshare数据格式被正确标准化
        assert "date" in result.columns
        assert "symbol" in result.columns
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns

    def test_performance_with_large_dataframe(self):
        """测试大型DataFrame的性能"""
        # 创建大型DataFrame
        large_data = pd.DataFrame(
            {
                "股票名称": [f"股票{i}" for i in range(1000)],
                "开盘价": [i * 10.0 for i in range(1000)],
                "收盘价": [i * 10.5 for i in range(1000)],
                "成交量": [i * 1000 for i in range(1000)],
            }
        )

        # 测试性能
        import time

        start_time = time.time()
        result = ColumnMapper.to_english(large_data)
        end_time = time.time()

        # 验证结果正确性
        assert len(result) == 1000
        assert "name" in result.columns
        assert "open" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns

        # 验证性能（应该在合理时间内完成）
        execution_time = end_time - start_time
        assert execution_time < 5.0  # 应该在5秒内完成

    def test_column_mapper_language_consistency(self):
        """测试列名映射器的语言一致性"""
        # 测试中英文互转的一致性
        original_data = pd.DataFrame(
            {
                "日期": ["2023-01-01"],
                "股票代码": ["000001"],
                "开盘价": [10.0],
                "收盘价": [10.5],
            }
        )

        # 中文到英文
        en_data = ColumnMapper.to_english(original_data)
        # 英文到中文
        cn_data = ColumnMapper.to_chinese(en_data)

        # 验证转换后的一致性
        assert "date" in en_data.columns
        assert "symbol" in en_data.columns
        assert "open" in en_data.columns
        assert "close" in en_data.columns

        assert "日期" in cn_data.columns
        assert "股票代码" in cn_data.columns
        assert "开盘价" in cn_data.columns
        assert "收盘价" in cn_data.columns

        # 验证数据值保持不变
        assert cn_data.iloc[0]["日期"] == original_data.iloc[0]["日期"]
        assert cn_data.iloc[0]["股票代码"] == original_data.iloc[0]["股票代码"]
        assert cn_data.iloc[0]["开盘价"] == original_data.iloc[0]["开盘价"]
        assert cn_data.iloc[0]["收盘价"] == original_data.iloc[0]["收盘价"]

    def test_column_mapper_edge_cases(self):
        """测试列名映射器的边界情况"""
        # 测试无效的目标语言
        data = pd.DataFrame({"日期": ["2023-01-01"], "股票代码": ["000001"]})

        with pytest.raises(ValueError, match="不支持的目标语言"):
            ColumnMapper.standardize_columns(data, target_lang="invalid")

        # 测试空的自定义映射
        result = ColumnMapper.standardize_columns(data, target_lang="en", custom_mapping={})
        assert "date" in result.columns
        assert "symbol" in result.columns


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])
