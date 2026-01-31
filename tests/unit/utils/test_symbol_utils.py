"""
Symbol Utils Test Suite
股票代码处理工具测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.symbol_utils (380行)
"""

import pytest

from src.utils.symbol_utils import (
    format_index_code_for_source,
    format_stock_code,
    format_stock_code_for_source,
    get_stock_exchange,
    is_valid_stock_code,
    normalize_index_code,
    normalize_stock_code,
)


class TestNormalizeStockCode:
    """股票代码标准化功能测试"""

    def test_normalize_basic_formats(self):
        """测试基本格式标准化"""
        # 6位数字格式
        assert normalize_stock_code("600000") == "600000"
        assert normalize_stock_code("000001") == "000001"
        assert normalize_stock_code("300001") == "300001"
        assert normalize_stock_code("688001") == "688001"

        # 整数格式 - 必须是6位数字
        assert normalize_stock_code(600000) == "600000"
        # 短于6位的数字会报错，不是有效格式
        with pytest.raises(ValueError):
            normalize_stock_code(1)

        # 浮点数格式 - 直接转换会包含小数点，导致无效
        with pytest.raises(ValueError):
            normalize_stock_code(600000.0)

    def test_normalize_with_exchange_suffixes(self):
        """测试带交易所后缀的格式"""
        # 后缀格式
        assert normalize_stock_code("600000.SH") == "600000"
        assert normalize_stock_code("000001.SZ") == "000001"
        assert normalize_stock_code("300001.SZ") == "300001"
        assert normalize_stock_code("688001.SH") == "688001"

    def test_normalize_with_exchange_prefixes(self):
        """测试带交易所前缀的格式"""
        # 前缀格式
        assert normalize_stock_code("sh600000") == "600000"
        assert normalize_stock_code("SZ000001") == "000001"  # 深圳代码
        assert normalize_stock_code("sz300001") == "300001"
        assert normalize_stock_code("SH688001") == "688001"

    def test_normalize_with_dot_separators(self):
        """测试带点分隔符的格式"""
        # 点分隔格式
        assert normalize_stock_code("sh.600000") == "600000"
        assert normalize_stock_code("sz.000001") == "000001"
        assert normalize_stock_code("SZ.300001") == "300001"
        assert normalize_stock_code("SH.688001") == "688001"

    def test_normalize_long_numbers(self):
        """测试长数字格式"""
        # 超过6位的数字，取最后6位
        assert normalize_stock_code("123456789") == "456789"
        assert normalize_stock_code("999999999") == "999999"

    def test_normalize_edge_cases(self):
        """测试边界情况"""
        # 带空格的输入
        assert normalize_stock_code(" 600000 ") == "600000"
        assert normalize_stock_code(" sz000001 ") == "000001"

        # 混合格式
        assert normalize_stock_code("sh.600000.SH") == "600000"

    def test_normalize_invalid_inputs(self):
        """测试无效输入"""
        # None值
        with pytest.raises(ValueError, match="股票代码不能为None"):
            normalize_stock_code(None)

        # 空字符串
        with pytest.raises(ValueError, match="股票代码不能为空"):
            normalize_stock_code("")
        with pytest.raises(ValueError, match="股票代码不能为空"):
            normalize_stock_code("   ")

        # 无效格式
        with pytest.raises(ValueError, match="无法识别的股票代码格式"):
            normalize_stock_code("abc")
        with pytest.raises(ValueError, match="无法识别的股票代码格式"):
            normalize_stock_code("12345")
        with pytest.raises(ValueError, match="无法识别的股票代码格式"):
            normalize_stock_code("invalid_code")


class TestGetStockExchange:
    """获取交易所功能测试"""

    def test_get_exchange_shanghai(self):
        """测试上海证券交易所"""
        assert get_stock_exchange("600000") == "SH"
        assert get_stock_exchange("688001") == "SH"
        assert get_stock_exchange("900001") == "SH"
        assert get_stock_exchange("sh600000") == "SH"
        assert get_stock_exchange("600000.SH") == "SH"

    def test_get_exchange_shenzhen(self):
        """测试深圳证券交易所"""
        assert get_stock_exchange("000001") == "SZ"
        assert get_stock_exchange("001001") == "SZ"
        assert get_stock_exchange("002001") == "SZ"
        assert get_stock_exchange("003001") == "SZ"
        assert get_stock_exchange("300001") == "SZ"
        assert get_stock_exchange("sz000001") == "SZ"
        assert get_stock_exchange("000001.SZ") == "SZ"

    def test_get_exchange_beijing(self):
        """测试北京证券交易所"""
        assert get_stock_exchange("430001") == "BJ"
        assert get_stock_exchange("800001") == "BJ"
        assert get_stock_exchange("830001") == "BJ"
        assert get_stock_exchange("870001") == "BJ"

    def test_get_exchange_default(self):
        """测试默认交易所"""
        # 无效代码默认返回上海
        assert get_stock_exchange("invalid") == "SH"

        # 不识别的首位默认返回上海
        assert get_stock_exchange("500001") == "SH"

    def test_get_exchange_with_invalid_code(self):
        """测试无效代码的交易所获取"""
        # 无效代码应该返回默认交易所（上海）
        assert get_stock_exchange("abc") == "SH"


class TestFormatStockCodeForSource:
    """根据数据源格式化股票代码测试"""

    def test_format_for_akshare(self):
        """测试AKShare格式化"""
        assert format_stock_code_for_source("600000", "akshare") == "600000"
        assert format_stock_code_for_source("sh600000", "akshare") == "600000"
        assert format_stock_code_for_source("600000.SH", "akshare") == "600000"
        assert format_stock_code_for_source("sz.000001", "akshare") == "000001"

    def test_format_for_baostock(self):
        """测试Baostock格式化"""
        assert format_stock_code_for_source("600000", "baostock") == "sh.600000"
        assert format_stock_code_for_source("000001", "baostock") == "sz.000001"
        assert format_stock_code_for_source("sh600000", "baostock") == "sh.600000"
        assert format_stock_code_for_source("sz.000001", "baostock") == "sz.000001"

    def test_format_for_invalid_source(self):
        """测试无效数据源类型"""
        with pytest.raises(ValueError, match="不支持的数据源类型"):
            format_stock_code_for_source("600000", "invalid")

        with pytest.raises(ValueError, match="不支持的数据源类型"):
            format_stock_code_for_source("600000", "tushare")

    def test_format_case_insensitive(self):
        """测试大小写不敏感"""
        assert format_stock_code_for_source("600000", "AKSHARE") == "600000"
        assert format_stock_code_for_source("600000", "Baostock") == "sh.600000"
        assert format_stock_code_for_source("600000", "BAOSTOCK") == "sh.600000"


class TestFormatStockCode:
    """股票代码格式化测试"""

    def test_format_numeric(self):
        """测试数字格式"""
        assert format_stock_code("sh600000", "numeric") == "600000"
        assert format_stock_code("600000.SH", "numeric") == "600000"
        assert format_stock_code(600000, "numeric") == "600000"

    def test_format_prefix(self):
        """测试前缀格式"""
        assert format_stock_code("600000", "prefix") == "sh600000"
        assert format_stock_code("000001", "prefix") == "sz000001"
        assert format_stock_code("688001", "prefix") == "sh688001"

    def test_format_suffix(self):
        """测试后缀格式"""
        assert format_stock_code("600000", "suffix") == "600000.SH"
        assert format_stock_code("000001", "suffix") == "000001.SZ"
        assert format_stock_code("688001", "suffix") == "688001.SH"

    def test_format_baostock(self):
        """测试Baostock格式"""
        assert format_stock_code("600000", "baostock") == "sh.600000"
        assert format_stock_code("000001", "baostock") == "sz.000001"
        assert format_stock_code("688001", "baostock") == "sh.688001"

    def test_format_akshare(self):
        """测试AKShare格式（与numeric相同）"""
        assert format_stock_code("sh600000", "akshare") == "600000"
        assert format_stock_code("sz000001", "akshare") == "000001"

    def test_format_invalid_type(self):
        """测试无效格式类型"""
        with pytest.raises(ValueError, match="不支持的格式类型"):
            format_stock_code("600000", "invalid")

    def test_format_case_insensitive(self):
        """测试大小写不敏感"""
        assert format_stock_code("600000", "NUMERIC") == "600000"
        assert format_stock_code("600000", "PREFIX") == "sh600000"
        assert format_stock_code("600000", "SUFFIX") == "600000.SH"


class TestIsValidStockCode:
    """股票代码有效性验证测试"""

    def test_is_valid_true_cases(self):
        """测试有效的股票代码"""
        valid_codes = [
            "600000",
            "000001",
            "300001",
            "688001",
            "sh600000",
            "SZ000001",
            "600000.SH",
            "sz.000001",
            600000,  # 整数
        ]

        for code in valid_codes:
            assert is_valid_stock_code(code), f"代码 {code} 应该是有效的"

    def test_is_valid_false_cases(self):
        """测试无效的股票代码"""
        invalid_codes = [
            None,
            "",
            "   ",
            "abc",
            "12345",
            "invalid_code",
            1,  # 短于6位的数字
            600000.0,  # 浮点数格式无效
        ]

        for code in invalid_codes:
            assert not is_valid_stock_code(code), f"代码 {code} 应该是无效的"

    def test_is_valid_long_numbers(self):
        """测试长数字（超过6位）应该有效"""
        # 超过6位的数字应该有效，会取最后6位
        assert is_valid_stock_code("999999999")  # 应该取"999999"
        assert is_valid_stock_code(123456789)  # 应该取"456789"


class TestNormalizeIndexCode:
    """指数代码标准化功能测试"""

    def test_normalize_shanghai_indices(self):
        """测试上证指数"""
        assert normalize_index_code("000001") == "000001"
        assert normalize_index_code("sh000001") == "000001"
        assert normalize_index_code("000001.SH") == "000001"
        assert normalize_index_code("sh.000001") == "000001"

    def test_normalize_shenzhen_indices(self):
        """测试深证指数"""
        assert normalize_index_code("399001") == "399001"
        assert normalize_index_code("sz399001") == "399001"
        assert normalize_index_code("399001.SZ") == "399001"
        assert normalize_index_code("sz.399001") == "399001"

    def test_normalize_long_index_codes(self):
        """测试长指数代码"""
        assert normalize_index_code("123456789") == "456789"

    def test_normalize_invalid_index_inputs(self):
        """测试无效指数代码输入"""
        with pytest.raises(ValueError, match="指数代码不能为None"):
            normalize_index_code(None)

        with pytest.raises(ValueError, match="指数代码不能为空"):
            normalize_index_code("")

        with pytest.raises(ValueError, match="无法识别的指数代码格式"):
            normalize_index_code("abc")


class TestFormatIndexCodeForSource:
    """指数代码根据数据源格式化测试"""

    def test_format_index_for_akshare(self):
        """测试AKShare指数格式化"""
        assert format_index_code_for_source("000001", "akshare") == "sh000001"
        assert format_index_code_for_source("399001", "akshare") == "sz399001"
        assert format_index_code_for_source("sh000001", "akshare") == "sh000001"

    def test_format_index_for_baostock(self):
        """测试Baostock指数格式化"""
        assert format_index_code_for_source("000001", "baostock") == "sh.000001"
        assert format_index_code_for_source("399001", "baostock") == "sz.399001"
        assert format_index_code_for_source("sh.000001", "baostock") == "sh.000001"

    def test_format_index_invalid_source(self):
        """测试无效数据源类型"""
        with pytest.raises(ValueError, match="不支持的数据源类型"):
            format_index_code_for_source("000001", "invalid")


class TestSymbolUtilsIntegration:
    """股票代码工具集成测试"""

    def test_complete_workflow_stock_code(self):
        """测试股票代码完整工作流程"""
        # 原始代码
        original = "sh.600000"

        # 标准化
        normalized = normalize_stock_code(original)
        assert normalized == "600000"

        # 获取交易所
        exchange = get_stock_exchange(normalized)
        assert exchange == "SH"

        # 为不同数据源格式化
        akshare_format = format_stock_code_for_source(normalized, "akshare")
        baostock_format = format_stock_code_for_source(normalized, "baostock")

        assert akshare_format == "600000"
        assert baostock_format == "sh.600000"

    def test_complete_workflow_index_code(self):
        """测试指数代码完整工作流程"""
        # 原始指数代码
        original = "sz.399001"

        # 标准化
        normalized = normalize_index_code(original)
        assert normalized == "399001"

        # 为不同数据源格式化
        akshare_format = format_index_code_for_source(normalized, "akshare")
        baostock_format = format_index_code_for_source(normalized, "baostock")

        assert akshare_format == "sz399001"
        assert baostock_format == "sz.399001"

    def test_format_compatibility(self):
        """测试格式化函数兼容性"""
        test_codes = ["600000", "000001", "sh600000", "sz.000001"]

        for code in test_codes:
            # format_stock_code应该与format_stock_code_for_source兼容
            akshare_1 = format_stock_code_for_source(code, "akshare")
            akshare_2 = format_stock_code(code, "akshare")

            baostock_1 = format_stock_code_for_source(code, "baostock")
            baostock_2 = format_stock_code(code, "baostock")

            assert akshare_1 == akshare_2
            assert baostock_1 == baostock_2

    def test_mixed_case_handling(self):
        """测试大小写混合处理"""
        mixed_cases = [
            "Sh600000",
            "SZ000001",
            "SH.600000",
            "Sz.000001",
            "Sh600000.sh",
            "SZ000001.SZ",
        ]

        for case in mixed_cases:
            # 所有输入都应该能正确处理
            normalized = normalize_stock_code(case)
            assert len(normalized) == 6
            assert normalized.isdigit()

            # 应该能获取交易所
            exchange = get_stock_exchange(normalized)
            assert exchange in ["SH", "SZ", "BJ"]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
