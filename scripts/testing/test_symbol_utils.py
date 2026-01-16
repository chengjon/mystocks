#!/usr/bin/env python3
"""
股票代码处理工具测试套件 - 完整覆盖symbol_utils模块
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import time
import concurrent.futures
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

# 导入被测试的模块
from src.utils.symbol_utils import (
    normalize_stock_code,
    get_stock_exchange,
    format_stock_code_for_source,
    format_stock_code,
    is_valid_stock_code,
    format_index_code_for_source,
    normalize_index_code,
)


class TestNormalizeStockCode:
    """normalize_stock_code函数测试类"""

    def test_basic_formats(self):
        """测试基本格式标准化"""
        # 6位纯数字
        assert normalize_stock_code("600000") == "600000"
        assert normalize_stock_code("000001") == "000001"

        # 带后缀格式
        assert normalize_stock_code("000001.SZ") == "000001"
        assert normalize_stock_code("600000.SH") == "000001"
        assert normalize_stock_code("600000.BJ") == "000001"

        # 带前缀格式
        assert normalize_stock_code("sz000001") == "000001"
        assert normalize_stock_code("SH600000") == "000001"
        assert normalize_stock_code("BJ600000") == "000001"

        # 点分隔格式
        assert normalize_stock_code("sz.000001") == "000001"
        assert normalize_stock_code("sh.600000") == "000000"

    def test_number_input_formats(self):
        """测试数字输入格式"""
        # 整数输入
        assert normalize_stock_code(600000) == "600000"
        assert normalize_stock_code(1) == "000001"

        # 浮点数输入
        assert normalize_stock_code(600000.0) == "600000"

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        assert normalize_stock_code("SZ000001") == "000001"
        assert normalize_stock_code("Sh600000") == "000001"
        assert normalize_stock_code("bJ600000") == "000001"

    def test_longer_codes(self):
        """测试超长代码截取"""
        # 超过6位的数字代码
        assert normalize_stock_code("1600000") == "600000"
        assert normalize_stock_code("123456789") == "234567"

    def test_special_formats(self):
        """测试特殊格式"""
        # 带空格
        assert normalize_stock_code(" 600000  ") == "600000"
        assert normalize_stock_code("\t600000\n") == "600000"

        # 混合格式
        assert normalize_stock_code("sh.000001.SZ") == "000001"

    def test_edge_cases(self):
        """测试边界情况"""
        # 6位数字（刚好标准）
        assert normalize_stock_code("123456") == "123456"

        # 只包含数字的混合字符串
        assert normalize_stock_code("abc600000xyz") == "600000"

    def test_error_cases(self):
        """测试错误情况"""
        # None值
        with pytest.raises(ValueError, match="股票代码不能为None"):
            normalize_stock_code(None)

        # 空字符串
        with pytest.raises(ValueError, match="股票代码不能为空或空白字符串"):
            normalize_stock_code("")

        # 空白字符串
        with pytest.raises(ValueError, match="股票代码不能为空或空白字符串"):
            normalize_stock_code("   ")

        # 无效格式
        with pytest.raises(ValueError, match="无法识别的股票代码格式"):
            normalize_stock_code("abcdef")

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        test_cases = [
            (" 600000 ", "600000"),
            ("\tsh.600000\n", "600000"),
            (" 000001.SZ  ", "000001"),
            ("   sz000001   ", "000001"),
        ]

        for input_code, expected in test_cases:
            result = normalize_stock_code(input_code)
            assert result == expected, (
                f"输入 '{input_code}' 期望 '{expected}' 得到 '{result}'"
            )


class TestGetStockExchange:
    """get_stock_exchange函数测试类"""

    def test_shanghai_exchange(self):
        """测试上海交易所识别"""
        assert get_stock_exchange("600000") == "SH"
        assert get_stock_exchange("600000.SH") == "SH"
        assert get_stock_exchange("sh600000") == "SH"
        assert get_stock_exchange("sh.600000") == "SH"
        assert get_stock_exchange("sh.600000.SH") == "SH"

    def test_shenzhen_exchange(self):
        """测试深圳交易所识别"""
        assert get_stock_exchange("000001") == "SZ"
        assert get_stock_exchange("000001.SZ") == "SZ"
        assert get_stock_exchange("sz000001") == "SZ"
        assert get_stock_exchange("sz.000001") == "SZ"

    def test_beijing_exchange(self):
        """测试北京交易所识别"""
        assert get_stock_exchange("430047") == "BJ"
        assert get_stock_exchange("430047.BJ") == "BJ"
        assert get_stock_exchange("bj430047") == "BJ"
        assert get_stock_exchange("bj.430047") == "BJ"

    def test_mixed_case_exchange(self):
        """测试大小写混合"""
        assert get_stock_exchange("Sh600000") == "SH"
        assert get_stock_exchange("SZ000001") == "SZ"
        assert get_stock_exchange("BJ600000") == "BJ"

    def test_number_input(self):
        """测试数字输入"""
        assert get_stock_exchange(600000) == "SH"
        assert get_stock_exchange(1) == "SZ"


class TestFormatStockCodeForSource:
    """format_stock_code_for_source函数测试类"""

    def test_akshare_format(self):
        """测试AKShare格式"""
        assert format_stock_code_for_source("600000", "akshare") == "600000"
        assert format_stock_code_for_source("000001", "akshare") == "000001"
        assert format_stock_code_for_source("600000.SH", "akshare") == "600000"

    def test_baostock_format(self):
        """测试Baostock格式"""
        assert format_stock_code_for_source("600000", "baostock") == "sh.600000"
        assert format_stock_code_for_source("000001", "baostock") == "sz.000001"
        assert format_stock_code_for_source("sh600000", "baostock") == "sh.600000"

    def test_tushare_format(self):
        """测试Tushare格式"""
        assert format_stock_code_for_source("600000", "tushare") == "600000.SH"
        assert format_stock_code_for_source("000001", "tushare") == "000001.SZ"
        assert format_stock_code_for_source("600000.SH", "tushare") == "600000.SH"

    def test_eastmoney_format(self):
        """测试EastMoney格式"""
        assert format_stock_code_for_source("600000", "eastmoney") == "600000"
        assert format_stock_code_for_source("000001", "eastmoney") == "000001"

    def test_invalid_source(self):
        """测试无效数据源"""
        with pytest.raises(ValueError, match="不支持的数据源格式"):
            format_stock_code_for_source("600000", "invalid_source")

    def test_mixed_case_input(self):
        """测试混合大小写输入"""
        assert format_stock_code_for_source("Sh600000", "baostock") == "sh.600000"
        assert format_stock_code_for_source("SZ000001", "baostock") == "sz.000001"


class TestFormatStockCode:
    """format_stock_code函数测试类"""

    def test_sh_suffix(self):
        """测试SH后缀"""
        assert format_stock_code("600000", "SH") == "600000.SH"
        assert format_stock_code("600000.SH", "SH") == "600000.SH"
        assert format_stock_code("sh600000", "SH") == "600000.SH"

    def test_sz_suffix(self):
        """测试SZ后缀"""
        assert format_stock_code("000001", "SZ") == "000001.SZ"
        assert format_stock_code("000001.SZ", "SZ") == "000001.SZ"
        assert format_stock_code("sz000001", "SZ") == "000001.SZ"

    def test_no_suffix(self):
        """测试无后缀"""
        assert format_stock_code("600000") == "600000"
        assert format_stock_code("000001") == "000001"

    def test_number_input(self):
        """测试数字输入"""
        assert format_stock_code(600000, "SH") == "600000.SH"
        assert format_stock_code(1, "SZ") == "000001.SZ"

    def test_invalid_exchange(self):
        """测试无效交易所代码"""
        with pytest.raises(ValueError, match="无效的交易所代码"):
            format_stock_code("600000", "INVALID")


class TestIsValidStockCode:
    """is_valid_stock_code函数测试类"""

    def test_valid_codes(self):
        """测试有效代码"""
        assert is_valid_stock_code("600000") == True
        assert is_valid_stock_code("000001") == True
        assert is_valid_stock_code("600000.SH") == True
        assert is_valid_stock_code("000001.SZ") == True
        assert is_valid_stock_code("sh600000") == True

    def test_invalid_codes(self):
        """测试无效代码"""
        assert is_valid_stock_code("") == False
        assert is_valid_stock_code("abcdef") == False
        assert is_valid_stock_code("123") == False
        assert is_valid_stock_code("1234567") == False

    def test_mixed_valid_invalid(self):
        """测试混合有效无效"""
        assert is_valid_stock_code("6000") == False  # 4位
        assert is_valid_stock_code("6000000") == False  # 7位
        assert is_valid_stock_code("600000.SHX") == False  # 错误后缀

    def test_special_characters(self):
        """测试特殊字符"""
        assert is_valid_stock_code("6000*0") == False
        assert is_valid_stock_code("6000 00") == False
        assert is_valid_stock_code("6000-00") == False

    def test_number_input(self):
        """测试数字输入"""
        assert is_valid_stock_code(600000) == True
        assert is_valid_stock_code(6000000) == False
        assert is_valid_stock_code(60000) == False


class TestFormatIndexCodeForSource:
    """format_index_code_for_source函数测试类"""

    def test_akshare_index_format(self):
        """测试AKShare指数格式"""
        assert format_index_code_for_source("000001", "akshare") == "000001"
        assert format_index_code_for_source("000001.SH", "akshare") == "000001"

    def test_baostock_index_format(self):
        """测试Baostock指数格式"""
        assert format_index_code_for_source("000001", "baostock") == "sh.000001"
        assert format_index_code_for_source("000001.SH", "baostock") == "sh.000001"

    def test_tushare_index_format(self):
        """测试Tushare指数格式"""
        assert format_index_code_for_source("000001", "tushare") == "000001.SH"
        assert format_index_code_for_source("000001.SZ", "tushare") == "000001.SZ"

    def test_invalid_index_source(self):
        """测试无效指数数据源"""
        with pytest.raises(ValueError, match="不支持的数据源格式"):
            format_index_code_for_source("000001", "invalid_source")


class TestNormalizeIndexCode:
    """normalize_index_code函数测试类"""

    def test_basic_index_formats(self):
        """测试基本指数格式"""
        assert normalize_index_code("000001") == "000001"
        assert normalize_index_code("000001.SH") == "000001"
        assert normalize_index_code("SH000001") == "000001"
        assert normalize_index_code("sh.000001") == "000001"

    def test_shanghai_index(self):
        """测试上海指数"""
        assert normalize_index_code("sh000001") == "000001"
        assert normalize_index_code("SH000001") == "000001"
        assert normalize_index_code("000001.SH") == "000001"

    def test_shenzhen_index(self):
        """测试深圳指数"""
        assert normalize_index_code("sz399001") == "399001"
        assert normalize_index_code("SZ399001") == "399001"
        assert normalize_index_code("399001.SZ") == "399001"

    def test_number_index_input(self):
        """测试数字指数输入"""
        assert normalize_index_code(1) == "000001"
        assert normalize_index_code(399001) == "399001"

    def test_index_code_extraction(self):
        """测试指数代码提取"""
        assert normalize_index_code("INDEXsh000001END") == "000001"
        assert normalize_index_code("DATA-sz399001-MORE") == "399001"


class TestEdgeCasesAndErrorHandling:
    """边界条件和异常处理测试类"""

    def test_none_input(self):
        """测试None输入"""
        with pytest.raises(ValueError, match="股票代码不能为None"):
            normalize_stock_code(None)

    def test_empty_string_input(self):
        """测试空字符串输入"""
        with pytest.raises(ValueError, match="股票代码不能为空或空白字符串"):
            normalize_stock_code("")

        with pytest.raises(ValueError, match="股票代码不能为空或空白字符串"):
            normalize_stock_code("   ")

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        assert normalize_stock_code("\t600000\n") == "600000"
        assert normalize_stock_code("  600000  ") == "600000"

    def test_invalid_format_error_message(self):
        """测试无效格式错误消息"""
        with pytest.raises(ValueError) as exc_info:
            normalize_stock_code("INVALID_FORMAT")

        error_msg = str(exc_info.value)
        assert "无法识别的股票代码格式" in error_msg
        assert "支持的格式示例" in error_msg

    def test_extremely_long_input(self):
        """测试极长输入"""
        long_code = "x" * 1000
        with pytest.raises(ValueError):
            normalize_stock_code(long_code)

    def test_float_edge_cases(self):
        """测试浮点数边界情况"""
        assert normalize_stock_code(600000.999) == "600000"
        assert normalize_stock_code(0.600000) == "600000"


class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_batch_processing_performance(self):
        """测试批量处理性能"""
        codes = ["600000", "000001", "000002", "600036", "601318"] * 100  # 500个代码
        start_time = time.time()

        results = [normalize_stock_code(code) for code in codes]

        elapsed = time.time() - start_time
        assert len(results) == len(codes)
        assert elapsed < 1.0  # 应该在1秒内完成
        assert all(result.isdigit() and len(result) == 6 for result in results)

    def test_concurrent_processing(self):
        """测试并发处理"""
        codes = ["600000", "000001", "000002"] * 50  # 150个代码

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(normalize_stock_code, code) for code in codes]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        assert len(results) == len(codes)
        assert all(result.isdigit() and len(result) == 6 for result in results)

    def test_repeated_operations_performance(self):
        """测试重复操作性能"""
        code = "600000.SH"
        iterations = 10000

        start_time = time.time()
        for _ in range(iterations):
            result = normalize_stock_code(code)
            # 重复标准化同一个代码
            normalized = normalize_stock_code(result)

        elapsed = time.time() - start_time
        assert elapsed < 2.0  # 10000次操作应该在2秒内完成


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_real_world_data_pipeline(self):
        """测试真实数据处理流水线"""
        # 模拟来自不同数据源的原始代码
        raw_codes = [
            "600000",  # 标准格式
            "000001.SZ",  # 后缀格式
            "sh600000",  # 前缀格式
            "sz.000001",  # 点分隔格式
            600000,  # 数字格式
            "SH600000.SH",  # 重复格式
        ]

        # 标准化处理
        normalized = [normalize_stock_code(code) for code in raw_codes]

        # 交易所识别
        exchanges = [get_stock_exchange(code) for code in raw_codes]

        # 验证结果
        assert all(len(code) == 6 and code.isdigit() for code in normalized)
        assert all(exchange in ["SH", "SZ"] for exchange in exchanges)

        # 数据源格式化
        akshare_codes = [
            format_stock_code_for_source(code, "akshare") for code in normalized
        ]
        baostock_codes = [
            format_stock_code_for_source(code, "baostock") for code in normalized
        ]

        assert len(akshare_codes) == len(normalized)
        assert len(baostock_codes) == len(normalized)

    def test_multi_source_code_conversion(self):
        """测试多源代码转换"""
        original_code = "600000"

        # 标准化
        normalized = normalize_stock_code(original_code)

        # 转换为不同格式
        baostock = format_stock_code_for_source(normalized, "baostock")
        tushare = format_stock_code_for_source(normalized, "tushare")
        eastmoney = format_stock_code_for_source(normalized, "eastmoney")

        # 验证可逆性
        assert normalize_stock_code(baostock) == normalized
        assert normalize_stock_code(tushare.split(".")[0]) == normalized

        # 验证格式正确性
        assert baostock == "sh.600000"
        assert tushare == "600000.SH"
        assert eastmoney == "600000"

    def test_error_recovery_in_pipeline(self):
        """测试流水线中的错误恢复"""
        mixed_codes = [
            "600000",  # 有效
            "000001",  # 有效
            "INVALID",  # 无效
            "sz000001",  # 有效
            "123",  # 无效
            "600001.SH",  # 有效
        ]

        processed = []
        errors = []

        for code in mixed_codes:
            try:
                normalized = normalize_stock_code(code)
                exchange = get_stock_exchange(code)
                processed.append((normalized, exchange))
            except ValueError as e:
                errors.append((code, str(e)))

        # 验证结果
        assert len(processed) == 4  # 4个有效代码
        assert len(errors) == 2  # 2个无效代码
        assert all(len(code) == 6 for code, _ in processed)

    def test_consistency_across_functions(self):
        """测试函数间的一致性"""
        test_cases = [
            "600000",
            "000001.SZ",
            "sh600000",
            "sz.000001",
            600000,
            1,
            600000.0,
        ]

        for input_code in test_cases:
            # 所有函数都应该接受相同的输入类型
            normalized = normalize_stock_code(input_code)
            is_valid = is_valid_stock_code(input_code)

            # 有效代码应该能正常处理
            if is_valid:
                assert len(normalized) == 6
                assert normalized.isdigit()

    def test_formatting_round_trip(self):
        """测试格式化往返转换"""
        original_codes = ["600000", "000001", "300750"]

        for original in original_codes:
            # 标准化
            normalized = normalize_stock_code(original)

            # 添加后缀再标准化
            with_suffix = format_stock_code(
                normalized, "SH" if normalized.startswith("6") else "SZ"
            )
            round_trip = normalize_stock_code(with_suffix)

            # 应该回到原始标准化结果
            assert round_trip == normalized


class TestUncoveredCodePaths:
    """专门测试未覆盖代码行的测试类"""

    def test_normalize_stock_code_line_82(self):
        """测试第82行：特殊格式处理分支"""
        # 测试点分隔格式的6位数字提取（第82行的return代码_str[2:]）
        assert normalize_stock_code("sz.600000") == "600000"
        assert normalize_stock_code("SH.000001") == "000001"

    def test_get_stock_exchange_line_123(self):
        """测试第123行：默认交易所分支"""
        # 测试不常见的股票代码第一位数字，触发默认"SH"分支
        assert get_stock_exchange("900001") == "SH"  # 以9开头
        assert get_stock_exchange("500001") == "SH"  # 以5开头
        assert get_stock_exchange("700001") == "SH"  # 以7开头

    def test_format_stock_code_lines_186_188_190_192(self):
        """测试第186, 188, 190, 192行：各种格式化分支"""
        # 使用有效的股票代码
        code = "600000"  # 上海股票

        # 第186行：prefix格式
        result_prefix = format_stock_code(code, "prefix")
        assert result_prefix == "sh600000"

        # 第188行：suffix格式
        result_suffix = format_stock_code(code, "suffix")
        assert result_suffix == "600000.SH"

        # 第190行：baostock格式
        result_baostock = format_stock_code(code, "baostock")
        assert result_baostock == "sh.600000"

        # 第192行：akshare格式
        result_akshare = format_stock_code(code, "akshare")
        assert result_akshare == "600000"

    def test_format_index_code_for_source_lines_237_238_240(self):
        """测试第237-240行：指数格式化的特殊分支"""
        # 测试上证指数分支（第236行）
        result = format_index_code_for_source("000001", "akshare")
        assert result == "sh000001"

        # 测试深证指数分支（第237-238行）
        result = format_index_code_for_source("399001", "akshare")
        assert result == "sz399001"

        # 测试默认分支（第240行）
        result = format_index_code_for_source("888888", "akshare")
        assert result == "sh888888"

    def test_normalize_index_code_lines_275_280(self):
        """测试第275, 280行：指数代码的异常处理"""
        # 第275行：None值检查
        with pytest.raises(ValueError) as exc_info:
            normalize_index_code(None)
        assert "指数代码不能为None" in str(exc_info.value)

        # 第280行：空字符串检查
        with pytest.raises(ValueError) as exc_info:
            normalize_index_code("")
        assert "指数代码不能为空或空白字符串" in str(exc_info.value)

        # 测试空白字符串
        with pytest.raises(ValueError) as exc_info:
            normalize_index_code("   ")
        assert "指数代码不能为空或空白字符串" in str(exc_info.value)

    def test_normalize_index_code_line_312(self):
        """测试第312行：长代码处理分支"""
        # 测试长于6位的代码，触发第311行的长度检查和第312行的截取
        assert normalize_index_code("123456789") == "456789"  # 取最后6位
        assert normalize_index_code("abcdef123456") == "123456"  # 取最后6位

    def test_normalize_stock_code_exact_line_82(self):
        """精确测试第82行的执行路径"""
        # 第82行处理特殊情况：指数代码格式，需要避开前面的所有条件
        # 关键：第59-67行的条件检查 len(code_str) >= 8 并且 market_part in ["SH", "SZ", "BJ"]
        # 第77-82行的条件检查 startswith(("SH", "SZ")) and len(code_str) == 8

        # 尝试构造一个能到达第82行但不被前面条件捕获的情况
        # 实际上，第77-82行是用于处理指数代码的特殊情况，如 SH000001, SZ399001
        # 这些在第59-67行可能不会被正确处理

        # 测试上证指数格式（应该在第77-82行处理）
        result = normalize_stock_code("SH000001")
        assert result == "000001"

        # 测试深证指数格式（应该在第77-82行处理）
        result = normalize_stock_code("SZ399001")
        assert result == "399001"

        # 验证这些确实触发了第82行的执行路径而不是前面的路径
        # 通过仔细构造，确保第82行被执行

    def test_integrated_coverage_with_valid_function_calls(self):
        """使用有效函数调用确保覆盖所有目标行"""
        # 确保所有未覆盖行都被有效测试覆盖

        # 1. normalize_stock_code 第82行
        assert normalize_stock_code("sz.600000") == "600000"

        # 2. get_stock_exchange 第123行默认分支
        assert get_stock_exchange("900001") == "SH"

        # 3. format_stock_code 第186, 188, 190, 192行
        code = "600000"
        assert format_stock_code(code, "prefix") == "sh600000"  # 第186行
        assert format_stock_code(code, "suffix") == "600000.SH"  # 第188行
        assert format_stock_code(code, "baostock") == "sh.600000"  # 第190行
        assert format_stock_code(code, "akshare") == "600000"  # 第192行

        # 4. format_index_code_for_source 第237-240行
        assert (
            format_index_code_for_source("000001", "akshare") == "sh000001"
        )  # 第236-237行
        assert (
            format_index_code_for_source("399001", "akshare") == "sz399001"
        )  # 第237-238行
        assert (
            format_index_code_for_source("888888", "akshare") == "sh888888"
        )  # 第240行

        # 5. normalize_index_code 第275, 280, 312行
        with pytest.raises(ValueError, match="指数代码不能为None"):
            normalize_index_code(None)  # 第275行

        with pytest.raises(ValueError, match="指数代码不能为空或空白字符串"):
            normalize_index_code("")  # 第280行

        assert normalize_index_code("123456789") == "456789"  # 第312行


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
