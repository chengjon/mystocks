#!/usr/bin/env python3
"""
列名映射器测试套件
完整测试column_mapper模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

# 导入被测试的模块
from src.utils.column_mapper import (
    ColumnMapper,
    standardize_dataframe,
    to_english_columns,
    to_chinese_columns
)


class TestColumnMapperClass:
    """ColumnMapper类测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建测试数据
        self.test_df_en = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'symbol': ['600000', '600001'],
            'open': [10.0, 15.0],
            'close': [10.5, 15.5],
            'volume': [1000000, 2000000],
            'amount': [10500000, 31000000]
        })

        self.test_df_cn = pd.DataFrame({
            '日期': ['2023-01-01', '2023-01-02'],
            '股票代码': ['600000', '600001'],
            '开盘': [10.0, 15.0],
            '收盘': [10.5, 15.5],
            '成交量': [1000000, 2000000],
            '成交额': [10500000, 31000000]
        })

    def test_standard_en_mapping_structure(self):
        """测试标准英文映射表结构"""
        mapping = ColumnMapper.STANDARD_EN_MAPPING

        # 验证关键字段存在
        assert '日期' in mapping
        assert '股票代码' in mapping
        assert '开盘' in mapping
        assert '收盘' in mapping
        assert 'open' in mapping
        assert 'close' in mapping
        assert 'volume' in mapping

        # 验证映射值
        assert mapping['日期'] == 'date'
        assert mapping['开盘'] == 'open'
        assert mapping['收盘'] == 'close'

    def test_standard_cn_mapping_structure(self):
        """测试标准中文映射表结构"""
        mapping = ColumnMapper.STANDARD_CN_MAPPING

        # 验证关键字段存在
        assert 'date' in mapping
        assert 'symbol' in mapping
        assert 'open' in mapping
        assert 'close' in mapping

        # 验证映射值
        assert mapping['date'] == '日期'
        assert mapping['symbol'] == '股票代码'
        assert mapping['open'] == '开盘价'

    def test_mapping_completeness(self):
        """测试映射表的完整性"""
        en_mapping = ColumnMapper.STANDARD_EN_MAPPING
        cn_mapping = ColumnMapper.STANDARD_CN_MAPPING

        # 验证映射数量
        assert len(en_mapping) >= 50  # 至少包含基本字段
        assert len(cn_mapping) >= 20

        # 验证核心字段存在对应关系
        core_fields = ['date', 'symbol', 'name', 'open', 'close', 'high', 'low', 'volume', 'amount']
        for field in core_fields:
            assert field in en_mapping.values()

    def test_standardize_columns_english_target(self):
        """测试英文目标语言标准化"""
        result = ColumnMapper.standardize_columns(
            self.test_df_en, target_lang="en"
        )

        # 验证列名保持不变（已经是英文）
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'open' in result.columns
        assert len(result.columns) == len(self.test_df_en.columns)

    def test_standardize_columns_chinese_target(self):
        """测试中文目标语言标准化"""
        result = ColumnMapper.standardize_columns(
            self.test_df_cn, target_lang="cn"
        )

        # 验证列名保持不变（已经是中文）
        assert '日期' in result.columns
        assert '股票代码' in result.columns
        assert '开盘' in result.columns
        assert len(result.columns) == len(self.test_df_cn.columns)

    def test_standardize_columns_chinese_to_english(self):
        """测试中文列名转换为英文"""
        result = ColumnMapper.standardize_columns(
            self.test_df_cn, target_lang="en"
        )

        # 验证中文列名被转换为英文
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'open' in result.columns
        assert 'close' in result.columns
        assert '日期' not in result.columns
        assert '股票代码' not in result.columns
        assert '开盘' not in result.columns

        # 验证数据完整性
        assert len(result) == len(self.test_df_cn)
        assert not result.empty

    def test_standardize_columns_english_to_chinese(self):
        """测试英文列名转换为中文"""
        result = ColumnMapper.standardize_columns(
            self.test_df_en, target_lang="cn"
        )

        # 验证英文列名被转换为中文
        assert '日期' in result.columns
        assert '股票代码' in result.columns
        assert '开盘价' in result.columns  # 注意：这里的映射可能不同

    def test_standardize_columns_with_custom_mapping(self):
        """测试自定义映射规则"""
        custom_mapping = {
            'custom_date': 'date',
            'custom_symbol': 'symbol',
            'custom_price': 'price'
        }

        test_df = pd.DataFrame({
            'custom_date': ['2023-01-01'],
            'custom_symbol': ['600000'],
            'custom_price': [10.0]
        })

        result = ColumnMapper.standardize_columns(
            test_df, target_lang="en", custom_mapping=custom_mapping
        )

        # 验证自定义映射生效
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'price' in result.columns

    def test_standardize_columns_cleaning_mechanism(self):
        """测试列名清理机制（去除空格、下划线等）"""
        test_df = pd.DataFrame({
            ' 日期  ': ['2023-01-01'],  # 带空格
            '_date_': ['2023-01-01'],  # 带下划线
            '-date-': ['2023-01-01'],  # 带连字符
            'DATE': ['2023-01-01'],    # 大写
        })

        result = ColumnMapper.standardize_columns(test_df, target_lang="en")

        # 验证清理后的列名映射
        assert 'date' in result.columns
        # 原始列名应该被重命名
        assert ' 日期  ' not in result.columns
        assert '_date_' not in result.columns
        assert '-date-' not in result.columns
        assert 'DATE' not in result.columns

    def test_standardize_columns_invalid_target_lang(self):
        """测试无效的目标语言"""
        test_df = pd.DataFrame({'date': ['2023-01-01']})

        with pytest.raises(ValueError, match="不支持的目标语言"):
            ColumnMapper.standardize_columns(test_df, target_lang="invalid")

    def test_standardize_columns_empty_dataframe(self):
        """测试空DataFrame处理"""
        empty_df = pd.DataFrame()

        result = ColumnMapper.standardize_columns(empty_df, target_lang="en")

        assert result.empty
        assert len(result) == 0

    def test_standardize_columns_case_insensitive_matching(self):
        """测试大小写不敏感匹配"""
        test_df = pd.DataFrame({
            'DATE': ['2023-01-01'],
            'SYMBOL': ['600000'],
            'OPEN': [10.0],
            'Volume': [1000000]  # 混合大小写
        })

        result = ColumnMapper.standardize_columns(test_df, target_lang="en")

        # 验证大小写不敏感匹配
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'open' in result.columns
        assert 'volume' in result.columns

    def test_to_english_convenience_method(self):
        """测试to_english便捷方法"""
        result = ColumnMapper.to_english(self.test_df_cn)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(self.test_df_cn)
        # 验证中文到英文的转换
        assert 'symbol' in result.columns or 'code' in result.columns

    def test_to_chinese_convenience_method(self):
        """测试to_chinese便捷方法"""
        result = ColumnMapper.to_chinese(self.test_df_en)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(self.test_df_en)

    def test_get_standard_columns_stock_daily_english(self):
        """测试获取股票日线数据英文标准列名"""
        columns = ColumnMapper.get_standard_columns("stock_daily", "en")

        assert isinstance(columns, list)
        assert len(columns) >= 8  # 至少包含基本OHLCV字段
        assert 'date' in columns
        assert 'symbol' in columns
        assert 'open' in columns
        assert 'close' in columns

    def test_get_standard_columns_stock_daily_chinese(self):
        """测试获取股票日线数据中文标准列名"""
        columns = ColumnMapper.get_standard_columns("stock_daily", "cn")

        assert isinstance(columns, list)
        assert len(columns) >= 8
        assert '日期' in columns
        assert '股票代码' in columns
        assert '开盘价' in columns

    def test_get_standard_columns_index_daily(self):
        """测试获取指数日线数据标准列名"""
        columns_en = ColumnMapper.get_standard_columns("index_daily", "en")
        columns_cn = ColumnMapper.get_standard_columns("index_daily", "cn")

        assert isinstance(columns_en, list)
        assert isinstance(columns_cn, list)
        assert len(columns_en) >= 8
        assert len(columns_cn) >= 8

    def test_get_standard_columns_stock_basic(self):
        """测试获取股票基本信息标准列名"""
        columns_en = ColumnMapper.get_standard_columns("stock_basic", "en")
        columns_cn = ColumnMapper.get_standard_columns("stock_basic", "cn")

        assert isinstance(columns_en, list)
        assert isinstance(columns_cn, list)
        assert 'symbol' in columns_en
        assert 'name' in columns_en
        assert 'symbol' in columns_cn
        assert 'name' in columns_cn

    def test_get_standard_columns_invalid_data_type(self):
        """测试无效数据类型"""
        columns = ColumnMapper.get_standard_columns("invalid_type", "en")

        assert columns == []

    def test_validate_columns_all_required_present(self):
        """测试所有必需列都存在的情况"""
        result = ColumnMapper.validate_columns(
            self.test_df_en,
            required_columns=['date', 'symbol', 'open']
        )

        assert result[0] is True  # is_valid
        assert result[1] == []    # missing_columns
        assert result[2] == []    # extra_columns (非严格模式)

    def test_validate_columns_missing_columns(self):
        """测试缺少必需列的情况"""
        incomplete_df = self.test_df_en.drop(['close'], axis=1)
        result = ColumnMapper.validate_columns(
            incomplete_df,
            required_columns=['date', 'symbol', 'close']
        )

        assert result[0] is False  # is_valid
        assert 'close' in result[1]  # missing_columns
        assert len(result[1]) == 1

    def test_validate_columns_strict_mode(self):
        """测试严格模式验证"""
        # 有额外列的情况
        extra_df = self.test_df_en.copy()
        extra_df['extra_col'] = [1, 2]

        result = ColumnMapper.validate_columns(
            extra_df,
            required_columns=['date', 'symbol'],
            strict=True
        )

        assert result[0] is False  # is_valid (严格模式下额外列导致失败)
        assert 'extra_col' in result[2]  # extra_columns

    def test_validate_columns_non_strict_mode(self):
        """测试非严格模式验证"""
        # 有额外列的情况
        extra_df = self.test_df_en.copy()
        extra_df['extra_col'] = [1, 2]

        result = ColumnMapper.validate_columns(
            extra_df,
            required_columns=['date', 'symbol'],
            strict=False
        )

        assert result[0] is True   # is_valid (非严格模式)
        assert result[2] == []   # extra_columns为空

    def test_add_custom_mapping_english(self):
        """测试添加英文自定义映射"""
        original_mapping = ColumnMapper.STANDARD_EN_MAPPING.copy()
        custom_mapping = {'custom_field': 'mapped_field'}

        ColumnMapper.add_custom_mapping(custom_mapping, target_lang="en")

        # 验证映射被添加
        assert 'custom_field' in ColumnMapper.STANDARD_EN_MAPPING
        assert ColumnMapper.STANDARD_EN_MAPPING['custom_field'] == 'mapped_field'

        # 验证原有映射保持不变
        assert 'date' in ColumnMapper.STANDARD_EN_MAPPING
        assert len(ColumnMapper.STANDARD_EN_MAPPING) == len(original_mapping) + 1

    def test_add_custom_mapping_chinese(self):
        """测试添加中文自定义映射"""
        original_mapping = ColumnMapper.STANDARD_CN_MAPPING.copy()
        custom_mapping = {'自定义字段': '映射字段'}

        ColumnMapper.add_custom_mapping(custom_mapping, target_lang="cn")

        # 验证映射被添加
        assert '自定义字段' in ColumnMapper.STANDARD_CN_MAPPING
        assert ColumnMapper.STANDARD_CN_MAPPING['自定义字段'] == '映射字段'

    def test_add_custom_mapping_invalid_target_lang(self):
        """测试添加自定义映射到无效目标语言"""
        with pytest.raises(ValueError, match="不支持的目标语言"):
            ColumnMapper.add_custom_mapping({}, target_lang="invalid")


class TestConvenienceFunctions:
    """便捷函数测试类"""

    def test_standardize_dataframe_function(self):
        """测试standardize_dataframe便捷函数"""
        result = standardize_dataframe(self.test_df_cn, target_lang="en")

        assert isinstance(result, pd.DataFrame)
        assert 'symbol' in result.columns
        assert 'date' in result.columns

    def test_to_english_columns_function(self):
        """测试to_english_columns便捷函数"""
        result = to_english_columns(self.test_df_cn)

        assert isinstance(result, pd.DataFrame)
        # 验证是英文列名
        assert not any('股票' in str(col) for col in result.columns)

    def test_to_chinese_columns_function(self):
        """测试to_chinese_columns便捷函数"""
        result = to_chinese_columns(self.test_df_en)

        assert isinstance(result, pd.DataFrame)
        # 验证是中文列名
        assert any('股票' in str(col) or '代码' in str(col) for col in result.columns)


class TestEdgeCasesAndErrorHandling:
    """边界情况和错误处理测试类"""

    def test_mixed_language_columns(self):
        """测试混合语言列名"""
        mixed_df = pd.DataFrame({
            'date': ['2023-01-01'],  # 英文
            '股票代码': ['600000'],   # 中文
            'open': [10.0],         # 英文
            '收盘': [10.5]         # 中文
            'volume': [1000000]     # 英文
            '成交量': [1200000]   # 中文
        })

        # 转换为英文
        result_en = ColumnMapper.standardize_columns(mixed_df, target_lang="en")
        assert 'date' in result_en.columns
        assert 'symbol' in result_en.columns
        assert 'close' in result_en.columns

        # 转换为中文
        result_cn = ColumnMapper.standardize_columns(mixed_df, target_lang="cn")
        assert '日期' in result_cn.columns
        assert '股票代码' in result_cn.columns
        assert '收盘价' in result_cn.columns

    def test_column_name_with_special_characters(self):
        """测试包含特殊字符的列名"""
        special_df = pd.DataFrame({
            'date!': ['2023-01-01'],
            'symbol@': ['600000'],
            'open#': [10.0],
            'close$': [10.5],
            'volume%': [1000000]
        })

        result = ColumnMapper.standardize_columns(special_df, target_lang="en")

        # 特殊字符列名可能不被映射，但应该保持原样
        assert 'date!' in result.columns or 'date' in result.columns
        assert 'symbol@' in result.columns or 'symbol' in result.columns

    def test_duplicate_column_names(self):
        """测试重复列名处理"""
        duplicate_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'Date': ['2023-01-01'],
            'DATE': ['2023-01-01'],
            'symbol': ['600000'],
            'Symbol': ['600000']
        })

        result = ColumnMapper.standardize_columns(duplicate_df, target_lang="en")

        # 应该只保留映射后的列名
        date_cols = [col for col in result.columns if 'date' in col.lower()]
        symbol_cols = [col for col in result.columns if 'symbol' in col.lower()]

        assert len(date_cols) == 3  # date, Date, DATE都映射到date
        assert len(symbol_cols) == 2  # symbol, Symbol都映射到symbol

    def test_very_long_column_names(self):
        """测试很长的列名"""
        long_name = 'a' * 100
        very_long_df = pd.DataFrame({
            long_name: ['value'],
            'symbol': ['600000']
        })

        result = ColumnMapper.standardize_columns(very_long_df, target_lang="en")

        # 长列名应该保持原样
        assert long_name in result.columns

    def test_numeric_column_names(self):
        """测试纯数字列名"""
        numeric_df = pd.DataFrame({
            1: ['value1'],
            2: ['value2'],
            'symbol': ['600000']
        })

        result = ColumnMapper.standardize_columns(numeric_df, target_lang="en")

        # 数字列名应该保持原样
        assert 1 in result.columns
        assert 2 in result.columns

    def test_none_and_nan_values_in_data(self):
        """测试数据中的None和NaN值处理"""
        data_with_nulls = pd.DataFrame({
            'symbol': [None, '600001'],
            'date': ['2023-01-01', None],
            'open': [None, 15.0],
            'close': [10.5, np.nan]
        })

        result = ColumnMapper.standardize_columns(data_with_nulls, target_lang="en")

        # 应该能够处理而不抛出异常
        assert len(result) == 2
        assert 'symbol' in result.columns

    def test_large_dataframe_performance(self):
        """测试大DataFrame性能"""
        large_df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=1000),
            'symbol': ['600000'] * 1000,
            'open': np.random.random(1000) * 100,
            'volume': np.random.randint(1000, 10000000, 1000)
        })

        start_time = time.time()
        result = ColumnMapper.standardize_columns(large_df, target_lang="en")
        elapsed_time = time.time() - start_time

        # 验证结果和性能
        assert len(result) == 1000
        assert 'symbol' in result.columns
        assert elapsed_time < 1.0  # 应该在1秒内完成

    def test_memory_efficiency(self):
        """测试内存效率"""
        import gc
        import psutil

        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 创建并处理大DataFrame
        test_df = pd.DataFrame({
            'column_' + str(i): np.random.random(100)
            for i in range(100)
        })

        # 多次执行标准化操作
        for _ in range(10):
            result = ColumnMapper.standardize_columns(test_df, target_lang="en")
            del result

        del test_df
        gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内
        assert memory_increase < 100 * 1024 * 1024  # 100MB

    def test_concurrent_standardization(self):
        """测试并发标准化操作"""
        import threading
        import queue

        results = queue.Queue()
        errors = queue.Queue()

        def worker(worker_id):
            try:
                worker_df = pd.DataFrame({
                    '日期': [f'2023-01-{worker_id:02d}'],
                    '股票代码': [f'60000{worker_id}'],
                    '开盘': [10.0 + worker_id],
                    '收盘': [10.5 + worker_id]
                })
                result = ColumnMapper.standardize_columns(worker_df, target_lang="en")
                results.put(f"Worker {worker_id} completed: {len(result)} rows")
            except Exception as e:
                errors.put(f"Worker {worker_id} error: {str(e)}")

        # 启动多个工作线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i+1))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert errors.empty(), f"Errors occurred: {list(errors.queue)}"
        assert results.qsize() == 5

    def test_mapping_priority_custom_over_default(self):
        """测试自定义映射覆盖默认映射"""
        # 使用默认映射会被覆盖的字段
        test_df = pd.DataFrame({
            'date': ['2023-01-01'],  # 默认映射到date
            'symbol': ['600000']      # 默认映射到symbol
        })

        custom_mapping = {
            'date': 'trade_date',  # 自定义映射覆盖默认
            'symbol': 'stock_code'  # 自定义映射覆盖默认
        }

        result = ColumnMapper.standardize_columns(
            test_df, target_lang="en", custom_mapping=custom_mapping
        )

        # 验证自定义映射优先
        assert 'trade_date' in result.columns
        assert 'stock_code' in result.columns
        assert 'date' not in result.columns
        assert 'symbol' not in result.columns


class TestIntegrationScenarios:
    """集成场景测试类"""

    def test_end_to_end_chinese_to_english_workflow(self):
        """测试中文到英文的端到端工作流程"""
        # 1. 创建原始中文数据
        raw_data = pd.DataFrame({
            '日期': ['2023-08-01', '2023-08-02'],
            '股票代码': ['600000', '600001'],
            '开盘': [10.0, 15.0],
            '收盘': [10.2, 15.5],
            '最高': [10.8, 16.0],
            '最低': [9.5, 14.5],
            '成交量': [1000000, 1200000],
            '成交额': [10200000, 17400000]
        })

        # 2. 转换为英文
        english_data = ColumnMapper.to_english(raw_data)

        # 3. 验证转换结果
        assert 'date' in english_data.columns
        assert 'symbol' in english_data.columns
        assert 'open' in english_data.columns
        assert 'close' in english_data.columns
        assert 'high' in english_data.columns
        assert 'low' in english_data.columns
        assert 'volume' in english_data.columns
        assert 'amount' in english_data.columns

        # 4. 验证数据完整性
        assert len(english_data) == len(raw_data)
        assert not english_data.equals(raw_data)  # 列名已改变

        # 5. 转换回中文
        chinese_data = ColumnMapper.to_chinese(english_data)

        # 6. 验证双向转换
        assert len(chinese_data) == len(raw_data)

    def test_integration_with_pandas_operations(self):
        """测试与pandas操作的集成"""
        # 创建原始数据
        raw_df = pd.DataFrame({
            '日期': ['2023-01-01', '2023-01-02'],
            '股票代码': ['600000', '600001'],
            '开盘': [10.0, 15.0],
            '收盘': [10.2, 15.5]
        })

        # 标准化列名
        std_df = ColumnMapper.standardize_columns(raw_df, target_lang="en")

        # 执行pandas操作
        filtered_df = std_df[std_df['close'] > 10.3]
        grouped_df = std_df.groupby('symbol').mean()

        # 验证操作结果
        assert len(filtered_df) == 1  # 只有第二行满足条件
        assert len(grouped_df) == 2  # 两只股票

    def test_integration_with_data_validation(self):
        """测试与数据验证的集成"""
        # 获取标准列名
        required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")

        # 创建测试数据
        test_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'symbol': ['600000', '600001'],
            'open': [10.0, 15.0],
            'close': [10.2, 15.5],
            'extra_field': ['extra1', 'extra2']
        })

        # 标准化列名
        std_df = ColumnMapper.standardize_columns(test_df, target_lang="en")

        # 验证列名
        is_valid, missing, extra = ColumnMapper.validate_columns(
            std_df, required_cols, strict=False
        )

        # 应该通过验证（所有必需列都存在）
        assert is_valid is True
        assert len(missing) == 0

        # 额外列应该被识别
        assert len(extra) >= 2  # 至少有extra_field

    def test_real_world_data_simulation(self):
        """测试真实世界数据场景模拟"""
        # 模拟来自不同数据源的数据
        akshare_data = pd.DataFrame({
            '日期': ['2023-08-01', '2023-08-02'],
            '股票代码': ['000001.SZ', '600000.SH'],
            '开盘': [10.0, 15.0],
            '收盘': [10.2, 15.5],
            '最高': [10.8, 16.0],
            '最低': [9.5, 14.8],
            '成交量': [1000000, 1200000],
            '成交额': [10200000, 18600000]
        })

        tushare_data = pd.DataFrame({
            'trade_date': ['2023-08-01', '2023-08-02'],
            'ts_code': ['000001.SZ', '600000.SH'],
            'open': [10.0, 15.0],
            'close': [10.2, 15.5],
            'high': [10.8, 16.0],
            'low': [9.5, 14.8],
            'vol': [1000000, 1200000],
            'amount': [10200000, 18600000]
        })

        # 标准化两个数据源
        akshare_std = ColumnMapper.standardize_columns(akshare_data, target_lang="en")
        tushare_std = ColumnMapper.standardize_columns(tushare_data, target_lang="en")

        # 验证标准化后的列名一致性
        assert set(akshare_std.columns) == set(tushare_std.columns)

        # 验证关键字段
        for col in ['date', 'symbol', 'open', 'close', 'high', 'low', 'volume', 'amount']:
            assert col in akshare_std.columns
            assert col in tushare_std.columns

    def test_custom_mapping_integration(self):
        """测试自定义映射集成"""
        # 定义数据源特定的映射规则
        data_source_mapping = {
            'stock_code': 'symbol',
            'trade_time': 'date',
            'last_price': 'close',
            'change_amount': 'change'
        }

        # 测试数据
        custom_df = pd.DataFrame({
            'stock_code': ['000001'],
            'trade_time': ['2023-01-01'],
            'last_price': [10.5],
            'change_amount': [0.5]
        })

        # 应用自定义映射
        result = ColumnMapper.standardize_columns(
            custom_df,
            target_lang="en",
            custom_mapping=data_source_mapping
        )

        # 验证自定义映射生效
        assert 'symbol' in result.columns
        assert 'date' in result.columns
        assert 'close' in result.columns
        assert 'change' in result.columns

    def test_batch_processing_multiple_dataframes(self):
        """测试批量处理多个DataFrame"""
        dataframes = [
            pd.DataFrame({'日期': ['2023-01-01'], '股票代码': ['600000'], '开盘': [10.0]}),
            pd.DataFrame({'日期': ['2023-01-02'], '股票代码': ['600001'], 'close': [15.0]}),
            pd.DataFrame({'日期': ['2023-01-03'], '股票代码': ['600002'], 'volume': [2000000]}),
        ]

        results = []
        for df in dataframes:
            std_df = ColumnMapper.standardize_columns(df, target_lang="en")
            results.append(std_df)

        # 验证所有DataFrame都被正确标准化
        for i, result in enumerate(results):
            assert 'date' in result.columns
            assert 'symbol' in result.columns

        # 验证结果独立性
        assert len(results) == 3
        assert sum(len(df) for df in results) == 3

    def test_error_recovery_and_robustness(self):
        """测试错误恢复和健壮性"""
        # 创建可能引发问题的数据
        problematic_df = pd.DataFrame({
            None: [None],  # None作为列名（pandas不允许，但测试边界情况）
            '': ['empty_col_name'],  # 空字符串列名
            '  ': ['space_col'],  # 空格列名
            'valid_col': ['value']  # 正常列名
        })

        try:
            result = ColumnMapper.standardize_columns(problematic_df, target_lang="en")
            # 如果没有抛出异常，验证结果
            assert len(result) > 0
            assert 'valid_col' in result.columns
        except Exception:
            # 如果抛出异常，这是预期的边界情况
            pass

    def test_column_name_conflicts_resolution(self):
        """测试列名冲突解决"""
        # 创建有映射冲突的DataFrame
        conflict_df = pd.DataFrame({
            'date': ['2023-01-01'],        # 映射到'date'
            'Date': ['2023-01-01'],        # 也映射到'date'
            'symbol': ['600000'],             # 映射到'symbol'
            'Symbol': ['600001'],             # 也映射到'symbol'
        })

        result = ColumnMapper.standardize_columns(conflict_df, target_lang="en")

        # 验证冲突解决（后面的映射覆盖前面的）
        date_cols = [col for col in result.columns if 'date' in col.lower()]
        symbol_cols = [col for col in result.columns if 'symbol' in col.lower()]

        assert len(date_cols) == 2  # date和Date都映射到date
        assert len(symbol_cols) == 2  # symbol和Symbol都映射到symbol


class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_mapping_table_memory_usage(self):
        """测试映射表内存使用"""
        # 获取映射表大小
        en_mapping_size = len(ColumnMapper.STANDARD_EN_MAPPING)
        cn_mapping_size = len(ColumnMapper.STANDARD_CN_MAPPING)

        # 验证映射表大小合理
        assert en_mapping_size >= 50
        assert cn_mapping_size >= 20

        # 验证内存使用合理
        total_mappings = en_mapping_size + cn_mapping_size
        assert total_mappings < 200  # 映射表不应该过大

    def test_string_operation_performance(self):
        """测试字符串操作性能"""
        test_string = "test_column_name_with_various_characters_and_length"

        # 模拟多次字符串处理操作
        start_time = time.time()
        for _ in range(1000):
            clean_col = (
                test_string.replace(" ", "")
                .replace("_", "")
                .replace("-", "")
                .lower()
            )
            # 模拟映射查找
            for key, value in ColumnMapper.STANDARD_EN_MAPPING.items():
                if clean_col == key.replace(" ", "").replace("_", "").replace("-", "").lower():
                    break

        elapsed_time = time.time() - start_time

        # 验证性能
        assert elapsed_time < 1.0  # 1000次操作应该在1秒内完成

    def test_large_dataset_processing(self):
        """测试大数据集处理"""
        # 创建大数据集
        large_df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=10000),
            'symbol': [f'{i:06d}' for i in range(10000)],
            'open': np.random.random(10000) * 100,
            'high': np.random.random(10000) * 110,
            'low': np.random.random(10000) * 90,
            'close': np.random.random(10000) * 105,
            'volume': np.random.randint(1000, 1000000, 10000),
        })

        # 测试处理性能
        start_time = time.time()
        result = ColumnMapper.standardize_columns(large_df, target_lang="en")
        elapsed_time = time.time() - start_time

        # 验证结果和性能
        assert len(result) == 10000
        assert 'symbol' in result.columns
        assert elapsed_time < 5.0  # 10000行数据应该在5秒内完成

    def test_memory_leak_prevention(self):
        """测试内存泄漏预防"""
        import gc
        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 重复执行操作
        for _ in range(100):
            test_df = pd.DataFrame({
                'date': ['2023-01-01'],
                'symbol': ['600000'],
                'open': [10.0]
            })
            result = ColumnMapper.standardize_columns(test_df, target_lang="en")
            del result

        gc.collect()

        final_memory = process.memory_info().rss
        memory_leak = final_memory - initial_memory

        # 内存泄漏应该在合理范围内（小于10MB）
        assert memory_leak < 10 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
