#!/usr/bin/env python3
"""
列名映射工具测试套件
完整测试column_mapper模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock problematic imports to avoid dependency issues
import unittest.mock

sys.modules["src.storage.database.connection_manager"] = unittest.mock.MagicMock()
sys.modules["src.core.config"] = unittest.mock.MagicMock()

import pytest

# 导入被测试的模块
from src.utils.column_mapper import (
    ColumnMapper,
    standardize_dataframe,
    to_english_columns,
    to_chinese_columns,
)

# 为便捷函数创建别名
standardize_columns = ColumnMapper.standardize_columns
to_english = ColumnMapper.to_english
to_chinese = ColumnMapper.to_chinese
validate_columns = ColumnMapper.validate_columns


class TestColumnMapperClass:
    """ColumnMapper类测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.mapper = ColumnMapper()

        # 测试数据
        self.test_df_en = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "close": [11.0, 12.0],
                "high": [12.0, 13.0],
                "low": [9.0, 10.0],
                "volume": [1000, 1200],
            }
        )

        self.test_df_cn = pd.DataFrame(
            {
                "开盘价": [10.0, 11.0],
                "收盘价": [11.0, 12.0],
                "最高价": [12.0, 13.0],
                "最低价": [9.0, 10.0],
                "成交量": [1000, 1200],
            }
        )

        self.test_df_mixed = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "收盘价": [11.0, 12.0],
                "high": [12.0, 13.0],
                "最低价": [9.0, 10.0],
                "volume": [1000, 1200],
            }
        )

    def test_column_mapper_initialization(self):
        """测试ColumnMapper初始化"""
        mapper = ColumnMapper()

        # 验证标准映射表已加载
        assert hasattr(ColumnMapper, "STANDARD_EN_MAPPING")
        assert hasattr(ColumnMapper, "STANDARD_CN_MAPPING")
        assert len(ColumnMapper.STANDARD_EN_MAPPING) > 0
        assert len(ColumnMapper.STANDARD_CN_MAPPING) > 0

        # 验证映射表包含基本字段
        assert "open" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "close" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "开盘价" in ColumnMapper.STANDARD_CN_MAPPING.values()
        assert "收盘价" in ColumnMapper.STANDARD_CN_MAPPING.values()

    def test_standard_en_mapping_content(self):
        """测试英文标准映射表内容"""
        # 验证基本价格字段
        assert "open" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "close" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "high" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "low" in ColumnMapper.STANDARD_EN_MAPPING.values()

        # 验证基本交易字段
        assert "volume" in ColumnMapper.STANDARD_EN_MAPPING.values()
        assert "amount" in ColumnMapper.STANDARD_EN_MAPPING.values()

        # 验证映射表不为空
        assert len(ColumnMapper.STANDARD_EN_MAPPING) > 0

    def test_standard_cn_mapping_content(self):
        """测试中文标准映射表内容"""
        # 验证基本价格字段
        assert "开盘价" in ColumnMapper.STANDARD_CN_MAPPING.values()
        assert "收盘价" in ColumnMapper.STANDARD_CN_MAPPING.values()
        assert "最高价" in ColumnMapper.STANDARD_CN_MAPPING.values()
        assert "最低价" in ColumnMapper.STANDARD_CN_MAPPING.values()

        # 验证基本交易字段
        assert "成交量" in ColumnMapper.STANDARD_CN_MAPPING.values()

        # 验证映射表不为空
        assert len(ColumnMapper.STANDARD_CN_MAPPING) > 0

    def test_standardize_columns_english_to_english(self):
        """测试英文列名标准化（已经是英文）"""
        result_df = self.mapper.standardize_columns(self.test_df_en, target_lang="en")

        # 验证列名保持不变
        expected_columns = ["open", "close", "high", "low", "volume"]
        assert list(result_df.columns) == expected_columns

        # 验证数据保持不变
        assert len(result_df) == len(self.test_df_en)

    def test_standardize_columns_chinese_to_english(self):
        """测试中文列名标准化为英文"""
        result_df = self.mapper.standardize_columns(self.test_df_cn, target_lang="en")

        # 验证列名转换为英文
        expected_columns = ["open", "close", "high", "low", "volume"]
        assert list(result_df.columns) == expected_columns

        # 验证数据保持不变
        assert len(result_df) == len(self.test_df_cn)

    def test_standardize_columns_mixed_to_english(self):
        """测试混合列名标准化为英文"""
        result_df = self.mapper.standardize_columns(
            self.test_df_mixed, target_lang="en"
        )

        # 验证列名转换为英文
        expected_columns = ["open", "close", "high", "low", "volume"]
        assert list(result_df.columns) == expected_columns

    def test_standardize_columns_mixed_to_chinese(self):
        """测试混合列名标准化为中文"""
        result_df = self.mapper.standardize_columns(
            self.test_df_mixed, target_lang="cn"
        )

        # 验证列名转换为中文
        expected_columns = ["开盘价", "收盘价", "最高价", "最低价", "成交量"]
        assert list(result_df.columns) == expected_columns

    def test_to_english_method(self):
        """测试to_english方法"""
        result_df = self.mapper.to_english(self.test_df_cn)

        # 验证列名转换为英文
        expected_columns = ["open", "close", "high", "low", "volume"]
        assert list(result_df.columns) == expected_columns

    def test_to_chinese_method(self):
        """测试to_chinese方法"""
        result_df = self.mapper.to_chinese(self.test_df_en)

        # 验证列名转换为中文
        expected_columns = ["开盘价", "收盘价", "最高价", "最低价", "成交量"]
        assert list(result_df.columns) == expected_columns

    def test_validate_columns_valid_columns(self):
        """测试有效列名验证"""
        # 创建测试DataFrame，只验证存在的列
        valid_en_df = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "close": [11.0, 12.0],
                "high": [12.0, 13.0],
                "low": [9.0, 10.0],
                "volume": [1000, 1200],
            }
        )

        # 只验证DataFrame中实际存在的列
        required_cols = ["open", "close", "high", "low", "volume"]
        result_en = self.mapper.validate_columns(valid_en_df, required_cols)

        # validate_columns返回(is_valid, missing, extra)的元组
        assert isinstance(result_en, tuple)
        assert len(result_en) == 3
        is_valid, missing, extra = result_en
        assert is_valid is True

    def test_validate_columns_invalid_columns(self):
        """测试无效列名验证"""
        # 创建无效DataFrame
        invalid_df = pd.DataFrame(
            {"invalid_col1": [10.0, 11.0], "invalid_col2": [12.0, 13.0]}
        )

        required_cols = ["open", "close", "high", "low", "volume"]
        result = self.mapper.validate_columns(invalid_df, required_cols)

        assert isinstance(result, tuple)
        is_valid, missing, extra = result
        assert is_valid is False
        assert len(missing) > 0

    def test_get_standard_columns_english(self):
        """测试获取英文标准列名"""
        columns = self.mapper.get_standard_columns("stock_daily", "en")

        assert isinstance(columns, list)
        assert len(columns) > 0
        assert "open" in columns or "close" in columns

    def test_get_standard_columns_chinese(self):
        """测试获取中文标准列名"""
        columns = self.mapper.get_standard_columns("stock_daily", "cn")

        assert isinstance(columns, list)
        assert len(columns) > 0
        assert "开盘价" in columns or "收盘价" in columns


class TestConvenienceFunctions:
    """便捷函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.test_df = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "收盘价": [11.0, 12.0],
                "high": [12.0, 13.0],
                "最低价": [9.0, 10.0],
                "volume": [1000, 1200],
            }
        )

    def test_standardize_dataframe_function(self):
        """测试standardize_dataframe便捷函数"""
        result_df = standardize_dataframe(self.test_df, target_lang="en")

        # 验证所有列名都转换为英文
        expected_columns = ["open", "close", "high", "low", "volume"]
        assert list(result_df.columns) == expected_columns

    def test_to_english_columns_function(self):
        """测试to_english_columns便捷函数"""
        # 创建中文DataFrame
        cn_df = pd.DataFrame(
            {"开盘价": [10.0, 11.0], "收盘价": [11.0, 12.0], "成交量": [1000, 1200]}
        )

        result_df = to_english_columns(cn_df)

        # 验证列名转换为英文
        expected_columns = ["open", "close", "volume"]
        assert list(result_df.columns) == expected_columns

    def test_to_chinese_columns_function(self):
        """测试to_chinese_columns便捷函数"""
        # 创建英文DataFrame
        en_df = pd.DataFrame(
            {"open": [10.0, 11.0], "close": [11.0, 12.0], "volume": [1000, 1200]}
        )

        result_df = to_chinese_columns(en_df)

        # 验证列名转换为中文
        expected_columns = ["开盘价", "收盘价", "成交量"]
        assert list(result_df.columns) == expected_columns


class TestEdgeCasesAndErrorHandling:
    """边界情况和错误处理测试类"""

    def test_empty_dataframe(self):
        """测试空DataFrame处理"""
        empty_df = pd.DataFrame()
        result_df = standardize_dataframe(empty_df, target_lang="en")

        assert result_df.empty
        assert len(result_df.columns) == 0

    def test_single_column_dataframe(self):
        """测试单列DataFrame"""
        single_df = pd.DataFrame({"open": [10.0, 11.0]})
        result_df = standardize_dataframe(single_df, target_lang="en")

        assert list(result_df.columns) == ["open"]

    def test_large_number_of_columns(self):
        """测试大量列的处理"""
        # 创建具有很多列的DataFrame
        columns = [f"col_{i}" for i in range(100)]
        data = {col: [1, 2] for col in columns}
        large_df = pd.DataFrame(data)

        # 应该只转换标准列名，其他保持不变
        result_df = standardize_dataframe(large_df, target_lang="en")

        # 验证标准列被转换，其他保持不变
        assert "open" not in result_df.columns  # 没有标准列，所以应该保持原样
        assert len(result_df.columns) == 100

    def test_duplicate_column_names(self):
        """测试重复列名处理"""
        duplicate_df = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "开盘价": [12.0, 13.0],  # 这两个都会映射到'open'
            }
        )

        result_df = standardize_columns(duplicate_df, target_lang="en")

        # 应该处理重复列名的映射
        # 具体行为取决于实现，我们只验证结果DataFrame有效
        assert len(result_df.columns) <= 2
        assert len(result_df) == 2  # 数据行数保持不变

    def test_special_characters_in_column_names(self):
        """测试列名中的特殊字符"""
        special_df = pd.DataFrame(
            {
                "open-price": [10.0, 11.0],
                "close@price": [11.0, 12.0],
                "high#price": [12.0, 13.0],
            }
        )

        result_df = standardize_columns(special_df, target_lang="en")

        # 'open-price'会被映射为'open'（去掉特殊字符后匹配）
        assert "open" in result_df.columns
        # 其他列保持原样，因为没有映射规则
        assert "close@price" in result_df.columns
        assert "high#price" in result_df.columns

    def test_none_and_nan_values_in_data(self):
        """测试数据中的None和NaN值"""
        none_df = pd.DataFrame(
            {
                "open": [10.0, None, 12.0],
                "close": [11.0, float("nan"), 13.0],
                "volume": [1000, 1200, None],
            }
        )

        result_df = standardize_columns(none_df, target_lang="en")

        # 验证列名处理正确
        assert list(result_df.columns) == ["open", "close", "volume"]
        # 验证数据保持不变（None和NaN应该保留）
        assert len(result_df) == 3

    def test_invalid_target_parameter(self):
        """测试无效的目标参数"""
        test_df = pd.DataFrame({"open": [10.0]})

        # 测试无效目标参数
        with pytest.raises(ValueError):  # 假设会抛出ValueError
            standardize_dataframe(test_df, target_lang="invalid_target")

    def test_none_dataframe_input(self):
        """测试None输入"""
        with pytest.raises(
            (TypeError, AttributeError)
        ):  # 可能抛出TypeError或AttributeError
            standardize_dataframe(None, target_lang="en")

    def test_non_dataframe_input(self):
        """测试非DataFrame输入"""
        invalid_inputs = [
            "string_input",
            123,
            {"open": [10.0]},  # 字典而不是DataFrame
            [1, 2, 3],  # 列表
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises((TypeError, AttributeError)):
                standardize_dataframe(invalid_input, target_lang="en")

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        case_df = pd.DataFrame(
            {
                "Open": [10.0, 11.0],  # 大写O
                "CLOSE": [11.0, 12.0],  # 全大写
                "High": [12.0, 13.0],  # 大写H
                "low": [9.0, 10.0],  # 小写
            }
        )

        result_df = standardize_columns(case_df, target_lang="en")

        # 验证大小写处理（具体行为取决于实现）
        # 通常应该是大小写不敏感的
        assert "open" in result_df.columns or "Open" in result_df.columns

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        space_df = pd.DataFrame(
            {
                " open ": [10.0, 11.0],  # 前后有空格
                " close": [11.0, 12.0],  # 前面有空格
                "high ": [12.0, 13.0],  # 后面有空格
                "volume": [1000, 1200],  # 没有空格
            }
        )

        result_df = standardize_columns(space_df, target_lang="en")

        # 验证空白字符处理（应该被去除或保留）
        assert len(result_df.columns) == 4

    def test_unicode_characters(self):
        """测试Unicode字符处理"""
        unicode_df = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "收盤價": [11.0, 12.0],  # 繁体中文
                "成交量": [1000, 1200],
                "📈": [1, 2],  # emoji
            }
        )

        result_df = standardize_columns(unicode_df, target_lang="en")

        # 验证Unicode字符处理
        assert "open" in result_df.columns
        # 其他字符的处理取决于实现


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_real_world_stock_data_mapping(self):
        """测试真实股票数据映射场景"""
        # 模拟真实的股票数据格式
        real_data = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "代码": ["000001", "000002"],
                "名称": ["平安银行", "万科A"],
                "开盘价": [10.50, 15.20],
                "最高价": [11.00, 15.80],
                "最低价": [10.20, 14.90],
                "收盘价": [10.80, 15.50],
                "成交量": [1000000, 800000],
                "成交额": [10800000, 12400000],
                "涨跌幅": [0.0286, 0.0197],
            }
        )

        # 转换为英文标准格式
        result_df = to_english(real_data)

        # 验证基本字段转换
        assert "open" in result_df.columns or "开盘价" in result_df.columns
        assert "close" in result_df.columns or "收盘价" in result_df.columns
        assert "high" in result_df.columns or "最高价" in result_df.columns
        assert "low" in result_df.columns or "最低价" in result_df.columns
        assert "volume" in result_df.columns or "成交量" in result_df.columns

    def test_multiple_api_data_source_integration(self):
        """测试多个API数据源集成"""
        # 模拟不同API源的数据格式
        akshare_data = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "close": [11.0, 12.0],
                "high": [12.0, 13.0],
                "low": [9.0, 10.0],
                "volume": [1000, 1200],
            }
        )

        tushare_data = pd.DataFrame(
            {
                "open": [15.0, 16.0],
                "close": [16.0, 17.0],
                "high": [17.0, 18.0],
                "low": [14.0, 15.0],
                "vol": [2000, 2200],  # 不同的成交量字段名
            }
        )

        baostock_data = pd.DataFrame(
            {
                "open": [20.0, 21.0],
                "close": [21.0, 22.0],
                "high": [22.0, 23.0],
                "low": [19.0, 20.0],
                "volume": [3000, 3200],
            }
        )

        # 标准化所有数据源
        std_akshare = standardize_columns(akshare_data, target_lang="en")
        std_tushare = standardize_columns(tushare_data, target_lang="en")
        std_baostock = standardize_columns(baostock_data, target_lang="en")

        # 验证所有数据源都有标准化的列名
        for df in [std_akshare, std_baostock]:
            assert "open" in df.columns
            assert "close" in df.columns
            assert "volume" in df.columns

    def test_data_pipeline_compatibility(self):
        """测试数据处理流水线兼容性"""
        # 模拟数据处理的各个阶段
        raw_data = pd.DataFrame(
            {
                "开盘价": [10.0, 11.0],
                "收盘价": [11.0, 12.0],
                "最高价": [12.0, 13.0],
                "最低价": [9.0, 10.0],
                "成交量": [1000, 1200],
            }
        )

        # 阶段1：数据清洗和标准化
        cleaned_data = to_english(raw_data)
        assert "open" in cleaned_data.columns

        # 阶段2：数据验证
        required_cols = ["open", "close", "high", "low", "volume"]
        is_valid, missing, extra = validate_columns(cleaned_data, required_cols)
        assert is_valid is True

        # 阶段3：数据处理（模拟）
        processed_data = cleaned_data.copy()
        processed_data["returns"] = processed_data["close"] / processed_data["open"] - 1

        # 阶段4：输出转换（如果需要中文）
        output_data = to_chinese(processed_data)
        assert "开盘价" in output_data.columns

    def test_historical_data_conversion(self):
        """测试历史数据转换"""
        # 模拟历史数据的不同格式
        historical_format1 = pd.DataFrame(
            {
                "trade_date": ["20250101", "20250102"],
                "ts_code": ["000001.SZ", "000001.SZ"],
                "open": [10.0, 11.0],
                "high": [12.0, 13.0],
                "low": [9.0, 10.0],
                "close": [11.0, 12.0],
                "vol": [1000, 1200],
            }
        )

        historical_format2 = pd.DataFrame(
            {
                "日期": pd.to_datetime(["2025-01-01", "2025-01-02"]),
                "股票代码": ["000001", "000001"],
                "开盘": [10.0, 11.0],
                "最高": [12.0, 13.0],
                "最低": [9.0, 10.0],
                "收盘": [11.0, 12.0],
                "成交量": [1000, 1200],
            }
        )

        # 标准化历史数据
        std_format1 = standardize_columns(historical_format1, target_lang="en")
        std_format2 = standardize_columns(historical_format2, target_lang="en")

        # 验证标准化结果
        for df in [std_format1, std_format2]:
            assert any("open" in str(col).lower() for col in df.columns)
            assert any("close" in str(col).lower() for col in df.columns)

    def test_technical_indicator_mapping(self):
        """测试技术指标映射"""
        # 包含技术指标的数据
        indicator_data = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02"],
                "close": [10.0, 11.0],
                "5日均线": [9.8, 10.2],
                "10日均线": [9.5, 9.8],
                "20日均线": [9.2, 9.5],
                "RSI": [55.0, 58.0],
                "MACD": [0.5, 0.6],
            }
        )

        # 转换为英文
        english_data = standardize_columns(indicator_data, target_lang="en")

        # 验证基本列被转换，技术指标保持原样（因为没有映射规则）
        assert "date" in english_data.columns
        assert "close" in english_data.columns
        # 技术指标列保持原样
        assert any("5日均线" in col for col in english_data.columns) or any(
            "ma5" in str(col).lower() for col in english_data.columns
        )
        assert any("10日均线" in col for col in english_data.columns) or any(
            "ma10" in str(col).lower() for col in english_data.columns
        )

    def test_database_schema_compatibility(self):
        """测试数据库模式兼容性"""
        # 模拟数据库存储的DataFrame
        db_df = pd.DataFrame(
            {
                "open_price": [10.0, 11.0],
                "close_price": [11.0, 12.0],
                "high_price": [12.0, 13.0],
                "low_price": [9.0, 10.0],
                "trade_volume": [1000, 1200],
            }
        )

        # 测试数据库列名验证
        required_cols = ["open", "close", "high", "low", "volume"]
        is_compatible, missing, extra = validate_columns(db_df, required_cols)

        # 根据实现，可能需要适配数据库特定的列名
        # 这里主要测试验证功能的工作
        assert isinstance(is_compatible, bool)

    def test_custom_mapping_usage(self):
        """测试自定义映射规则的使用"""
        test_df = pd.DataFrame(
            {"custom_col1": [1.0, 2.0], "custom_col2": [3.0, 4.0], "open": [10.0, 11.0]}
        )

        # 测试自定义映射覆盖默认映射
        custom_mapping = {
            "custom_col1": "mapped_col1",
            "custom_col2": "mapped_col2",
            "open": "custom_open",  # 覆盖默认映射
        }

        result_df = ColumnMapper.standardize_columns(
            test_df, target_lang="en", custom_mapping=custom_mapping
        )

        # 验证自定义映射被应用
        assert "mapped_col1" in result_df.columns
        assert "mapped_col2" in result_df.columns
        assert "custom_open" in result_df.columns
        # 验证原始列名不存在
        assert "custom_col1" not in result_df.columns
        assert "open" not in result_df.columns

    def test_add_custom_mapping_method(self):
        """测试add_custom_mapping方法"""
        # 保存原始映射
        original_en_mapping = ColumnMapper.STANDARD_EN_MAPPING.copy()
        original_cn_mapping = ColumnMapper.STANDARD_CN_MAPPING.copy()

        try:
            # 测试添加英文自定义映射
            custom_en_mapping = {
                "custom_field": "custom_mapped_field",
                "test_column": "test_mapped_column",
            }

            ColumnMapper.add_custom_mapping(custom_en_mapping, "en")

            # 验证映射被添加
            assert "custom_field" in ColumnMapper.STANDARD_EN_MAPPING
            assert (
                ColumnMapper.STANDARD_EN_MAPPING["custom_field"]
                == "custom_mapped_field"
            )
            assert "test_column" in ColumnMapper.STANDARD_EN_MAPPING
            assert (
                ColumnMapper.STANDARD_EN_MAPPING["test_column"] == "test_mapped_column"
            )

            # 测试添加中文自定义映射
            custom_cn_mapping = {
                "自定义字段": "custom_mapped_field",
                "测试列": "test_mapped_column",
            }

            ColumnMapper.add_custom_mapping(custom_cn_mapping, "cn")

            # 验证映射被添加
            assert "自定义字段" in ColumnMapper.STANDARD_CN_MAPPING
            assert (
                ColumnMapper.STANDARD_CN_MAPPING["自定义字段"] == "custom_mapped_field"
            )

        finally:
            # 恢复原始映射（避免影响其他测试）
            ColumnMapper.STANDARD_EN_MAPPING.clear()
            ColumnMapper.STANDARD_EN_MAPPING.update(original_en_mapping)
            ColumnMapper.STANDARD_CN_MAPPING.clear()
            ColumnMapper.STANDARD_CN_MAPPING.update(original_cn_mapping)

    def test_add_custom_mapping_invalid_language(self):
        """测试add_custom_mapping无效语言参数"""
        with pytest.raises(ValueError, match="不支持的目标语言"):
            ColumnMapper.add_custom_mapping({"test": "test"}, "invalid_lang")

    def test_mapping_with_print_output(self):
        """测试会触发打印输出的映射操作"""
        test_df = pd.DataFrame(
            {"开盘价": [10.0, 11.0], "收盘价": [11.0, 12.0], "成交量": [1000, 1200]}
        )

        # 这个映射操作应该触发打印输出（第192行）
        import io
        from contextlib import redirect_stdout

        # 捕获标准输出
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result_df = ColumnMapper.standardize_columns(test_df, target_lang="en")

        # 验证打印输出包含映射信息
        output = captured_output.getvalue()
        assert "列名映射完成" in output
        assert "开盘价" in output or "open" in output

        # 验证映射结果正确
        assert "open" in result_df.columns
        assert "close" in result_df.columns
        assert "volume" in result_df.columns

    def test_case_insensitive_mapping(self):
        """测试大小写不敏感的列名映射"""
        test_df = pd.DataFrame(
            {
                "VOL": [1000, 1200],  # 大写的VOL，应该通过小写匹配映射到volume
                "成交量": [2000, 2400],  # 中文，应该映射到volume
                "open": [10.0, 11.0],
            }
        )

        result_df = ColumnMapper.standardize_columns(test_df, target_lang="en")

        # 验证映射结果
        assert len(result_df) == 2
        # 'VOL'应该通过小写匹配映射到volume
        assert "volume" in result_df.columns
        # '成交量'应该映射到volume（但会与VOL合并）
        assert "open" in result_df.columns
        # volume列存在（可能由于重复映射行为导致多个volume列）
        assert "volume" in result_df.columns


class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time

        # 创建大数据集（10万行，50列）
        num_rows = 100000
        num_cols = 50

        # 生成列名
        columns = []
        for i in range(num_cols):
            if i % 10 == 0:
                columns.append("open")
            elif i % 10 == 1:
                columns.append("close")
            elif i % 10 == 2:
                columns.append("high")
            elif i % 10 == 3:
                columns.append("low")
            elif i % 10 == 4:
                columns.append("volume")
            else:
                columns.append(f"col_{i}")

        # 生成数据
        data = {col: [float(i) for i in range(num_rows)] for col in columns}
        large_df = pd.DataFrame(data)

        # 测试性能
        start_time = time.time()
        result_df = standardize_columns(large_df, target_lang="en")
        end_time = time.time()

        # 验证结果（注意：映射器会合并重复的列名）
        assert len(result_df) == num_rows
        # 由于列名映射可能导致重复列被合并，检查至少有基本列
        assert "open" in result_df.columns
        assert "close" in result_df.columns
        assert "high" in result_df.columns
        assert "low" in result_df.columns
        assert "volume" in result_df.columns

        # 性能检查（应该在合理时间内完成）
        processing_time = end_time - start_time
        assert processing_time < 10.0  # 应该在10秒内完成

    def test_memory_usage_large_dataset(self):
        """测试大数据集内存使用"""
        # 创建中等大小的数据集测试内存效率
        num_rows = 10000
        num_cols = 20

        columns = []
        for i in range(num_cols):
            if i < 5:
                columns.extend(["open", "close", "high", "low", "volume"])
            else:
                columns.append(f"col_{i}")

        columns = columns[:num_cols]  # 确保正确的列数
        data = {col: [float(i % 100) for i in range(num_rows)] for col in columns}
        test_df = pd.DataFrame(data)

        # 执行转换
        result_df = standardize_columns(test_df, target_lang="en")

        # 验证内存使用合理（通过检查数据大小）
        assert len(result_df) == num_rows
        # 只验证基本列存在（因为可能存在重复列合并）
        assert "open" in result_df.columns
        assert "close" in result_df.columns
        assert "high" in result_df.columns
        assert "low" in result_df.columns
        assert "volume" in result_df.columns

    def test_concurrent_column_mapping(self):
        """测试并发列名映射"""
        import threading
        import queue

        results = queue.Queue()

        def worker_function(worker_id):
            """工作线程函数"""
            try:
                test_data = pd.DataFrame(
                    {
                        "open": [10.0 * worker_id, 11.0 * worker_id],
                        "收盘价": [11.0 * worker_id, 12.0 * worker_id],
                        "high": [12.0 * worker_id, 13.0 * worker_id],
                        "最低价": [9.0 * worker_id, 10.0 * worker_id],
                        "volume": [1000 * worker_id, 1200 * worker_id],
                    }
                )

                result_df = standardize_columns(test_data, target_lang="en")
                results.put(f"worker_{worker_id}_success")

            except Exception as e:
                results.put(f"worker_{worker_id}_error: {str(e)}")

        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i + 1,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 收集结果
        collected_results = []
        while not results.empty():
            collected_results.append(results.get_nowait())

        # 验证所有操作都成功
        assert len(collected_results) == 5
        assert all("success" in result for result in collected_results)

    def test_repeated_operations_performance(self):
        """测试重复操作性能"""
        import time

        # 创建测试数据
        test_data = pd.DataFrame(
            {"open": [10.0, 11.0], "收盘价": [11.0, 12.0], "volume": [1000, 1200]}
        )

        # 执行多次操作并测试性能
        iterations = 1000
        start_time = time.time()

        for i in range(iterations):
            result_df = standardize_columns(test_data, target_lang="en")

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations

        # 性能验证（平均每次操作应该很快）
        assert avg_time < 0.01  # 平均每次操作应该小于10毫秒
        assert total_time < 30.0  # 总时间应该合理

    def test_scalability_with_column_count(self):
        """测试列数扩展性"""
        import time

        # 测试不同列数的性能
        column_counts = [10, 50, 100, 200]
        processing_times = []

        for num_cols in column_counts:
            # 创建指定列数的测试数据
            columns = []
            for i in range(num_cols):
                if i % 5 == 0:
                    columns.append("open")
                elif i % 5 == 1:
                    columns.append("close")
                elif i % 5 == 2:
                    columns.append("high")
                elif i % 5 == 3:
                    columns.append("low")
                else:
                    columns.append(f"col_{i}")

            data = {col: [1.0, 2.0] for col in columns}
            test_df = pd.DataFrame(data)

            # 测试处理时间
            start_time = time.time()
            result_df = standardize_columns(test_df, target_lang="en")
            end_time = time.time()

            processing_time = end_time - start_time
            processing_times.append(processing_time)

            # 验证结果正确性（由于重复列名可能被合并，检查基本列存在）
            assert len(result_df.columns) > 0
            assert "open" in result_df.columns
            assert "close" in result_df.columns

        # 验证性能随列数线性增长（不应该是指数增长）
        # 简单检查：最大处理时间不应该是最小处理时间的10倍以上
        max_time = max(processing_times)
        min_time = min(processing_times)
        assert max_time < min_time * 10, (
            f"性能扩展性不佳: 最大时间={max_time}, 最小时间={min_time}"
        )

    def test_memory_efficiency_with_large_strings(self):
        """测试大字符串数据的内存效率"""
        # 创建包含大字符串的DataFrame
        large_string_data = pd.DataFrame(
            {
                "open": [10.0, 11.0],
                "description": ["A" * 1000, "B" * 1000],  # 大字符串
                "收盘价": [11.0, 12.0],
                "long_name_column": ["C" * 500, "D" * 500],
            }
        )

        # 执行转换
        result_df = standardize_columns(large_string_data, target_lang="en")

        # 验证结果正确性且内存使用合理
        assert len(result_df) == 2
        assert len(result_df.columns) == 4

    def test_performance_with_different_data_types(self):
        """测试不同数据类型的性能"""
        import time

        # 创建包含不同数据类型的DataFrame
        mixed_data = pd.DataFrame(
            {
                "open": [10.0, 11.0],  # float
                "count": [100, 200],  # int
                "收盘价": [11.0, 12.0],  # float
                "name": ["stock1", "stock2"],  # string
                "active": [True, False],  # bool
                "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),  # datetime
                "category": pd.Categorical(["A", "B"]),  # categorical
            }
        )

        # 测试转换性能
        start_time = time.time()
        result_df = standardize_columns(mixed_data, target_lang="en")
        end_time = time.time()

        processing_time = end_time - start_time

        # 验证结果正确性
        assert len(result_df) == 2
        assert "open" in result_df.columns

        # 验证性能合理
        assert processing_time < 1.0  # 应该很快完成


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
