"""
TDX 二进制文件读取功能测试

测试 TdxAdapter.read_day_file() 方法

作者: MyStocks Development Team
创建日期: 2025-10-19
"""

import pytest
import pandas as pd
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.tdx_adapter import TdxDataSource


class TestTdxBinaryRead:
    """TDX 二进制文件读取测试类"""

    @pytest.fixture
    def tdx_adapter(self):
        """创建 TdxAdapter 实例"""
        return TdxDataSource()

    @pytest.fixture
    def test_day_file(self):
        """测试文件路径"""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "temp/pyprof/data/sh000001.day"
        )

    def test_read_day_file_basic(self, tdx_adapter, test_day_file):
        """测试基本读取功能"""
        # 跳过如果文件不存在
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        # 读取文件
        df = tdx_adapter.read_day_file(test_day_file)

        # 验证返回类型
        assert isinstance(df, pd.DataFrame), "返回值应为 DataFrame"

        # 验证不为空
        assert not df.empty, "返回的 DataFrame 不应为空"

        # 验证列名
        expected_columns = [
            "code",
            "tradeDate",
            "open",
            "high",
            "low",
            "close",
            "amount",
            "vol",
        ]
        assert (
            list(df.columns) == expected_columns
        ), f"列名不匹配,期望{expected_columns}"

        print(f"✅ 测试通过: 读取了 {len(df)} 条记录")
        print(f"   列名: {list(df.columns)}")
        print(f"   数据形状: {df.shape}")

    def test_read_day_file_data_types(self, tdx_adapter, test_day_file):
        """测试数据类型正确性"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        df = tdx_adapter.read_day_file(test_day_file)

        # 验证 code 列
        assert df["code"].dtype == object, "code 应为字符串类型"

        # 验证价格列为数值类型
        for col in ["open", "high", "low", "close"]:
            assert pd.api.types.is_numeric_dtype(df[col]), f"{col} 应为数值类型"

        # 验证成交量和成交额为数值类型
        assert pd.api.types.is_numeric_dtype(df["amount"]), "amount 应为数值类型"
        assert pd.api.types.is_numeric_dtype(df["vol"]), "vol 应为数值类型"

        print("✅ 测试通过: 数据类型正确")

    def test_read_day_file_data_validity(self, tdx_adapter, test_day_file):
        """测试数据有效性"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        df = tdx_adapter.read_day_file(test_day_file)

        # 验证价格为正数
        for col in ["open", "high", "low", "close"]:
            assert (df[col] > 0).all(), f"{col} 应全部为正数"

        # 验证最高价 >= 最低价
        assert (df["high"] >= df["low"]).all(), "最高价应 >= 最低价"

        # 验证最高价 >= 收盘价
        assert (df["high"] >= df["close"]).all(), "最高价应 >= 收盘价"

        # 验证最低价 <= 收盘价
        assert (df["low"] <= df["close"]).all(), "最低价应 <= 收盘价"

        print("✅ 测试通过: 数据有效性检查通过")

    def test_read_day_file_stock_code(self, tdx_adapter, test_day_file):
        """测试股票代码提取"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        df = tdx_adapter.read_day_file(test_day_file)

        # 验证股票代码
        expected_code = "sh000001"
        assert df["code"].iloc[0] == expected_code, f"股票代码应为 {expected_code}"
        assert df["code"].nunique() == 1, "所有记录的股票代码应相同"

        print(f"✅ 测试通过: 股票代码 = {df['code'].iloc[0]}")

    def test_read_day_file_date_format(self, tdx_adapter, test_day_file):
        """测试日期格式"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        df = tdx_adapter.read_day_file(test_day_file)

        # 验证日期格式 (应为8位字符串 YYYYMMDD)
        assert df["tradeDate"].dtype == object, "tradeDate 应为字符串类型"
        assert df["tradeDate"].str.len().iloc[0] == 8, "日期应为8位字符串"

        # 尝试转换为日期
        pd.to_datetime(df["tradeDate"], format="%Y%m%d")

        print("✅ 测试通过: 日期格式正确")
        print(f"   第一条记录日期: {df['tradeDate'].iloc[0]}")
        print(f"   最后一条记录日期: {df['tradeDate'].iloc[-1]}")

    def test_read_day_file_not_found(self, tdx_adapter):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            tdx_adapter.read_day_file("/nonexistent/path/file.day")

        print("✅ 测试通过: 文件不存在时抛出正确异常")

    def test_read_day_file_statistics(self, tdx_adapter, test_day_file):
        """测试数据统计信息"""
        if not os.path.exists(test_day_file):
            pytest.skip(f"测试文件不存在: {test_day_file}")

        df = tdx_adapter.read_day_file(test_day_file)

        print("\n=== 数据统计信息 ===")
        print(f"记录总数: {len(df)}")
        print(f"股票代码: {df['code'].iloc[0]}")
        print(f"日期范围: {df['tradeDate'].iloc[0]} - {df['tradeDate'].iloc[-1]}")
        print("\n价格统计:")
        print(df[["open", "high", "low", "close"]].describe())
        print("\n成交量统计:")
        print(df[["amount", "vol"]].describe())

        print("\n前5条记录:")
        print(df.head())


if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "-s"])
