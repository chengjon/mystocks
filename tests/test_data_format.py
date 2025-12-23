#!/usr/bin/env python3
"""
测试数据格式转换中间件
"""

import sys

# 添加项目根目录到Python路径
sys.path.insert(0, "/opt/claude/mystocks_spec")

# 导入数据格式转换模块
from src.utils.data_format_converter import (
    normalize_stock_data_format,
    normalize_api_response_format,
)
import pandas as pd


def test_data_format_conversion():
    """测试数据格式转换功能"""
    print("测试数据格式转换中间件...")

    # 创建测试数据（模拟数据库中的snake_case字段）
    test_data = pd.DataFrame(
        {
            "symbol": ["000001.SZ", "600000.SH"],
            "name": ["平安银行", "浦发银行"],
            "industry": ["金融", "金融"],
            "area": ["深圳", "上海"],
            "market": ["SZ", "SH"],
            "list_date": ["2025-01-01", "2025-01-02"],
        }
    )

    print("1. 原始数据 (数据库格式 - snake_case):")
    print(test_data)
    print("列名:", list(test_data.columns))

    # 标准化数据格式
    normalized_data = normalize_stock_data_format(test_data)

    print("\n2. 标准化后数据 (统一格式):")
    print(normalized_data)
    print("列名:", list(normalized_data.columns))

    # 测试API响应格式标准化
    api_response = {
        "data": normalized_data.to_dict("records"),
        "total": len(normalized_data),
    }

    print("\n3. 原始API响应:")
    print(api_response)

    normalized_response = normalize_api_response_format(api_response)

    print("\n4. 标准化后API响应:")
    print(normalized_response)

    # 检查字段一致性
    print("\n5. 字段一致性检查:")
    expected_fields = ["symbol", "name", "industry", "area", "market", "list_date"]
    actual_fields = list(normalized_data.columns)

    missing_fields = set(expected_fields) - set(actual_fields)
    extra_fields = set(actual_fields) - set(expected_fields)

    if not missing_fields and not extra_fields:
        print("✅ 字段一致性检查通过")
    else:
        if missing_fields:
            print(f"❌ 缺失字段: {missing_fields}")
        if extra_fields:
            print(f"⚠️  额外字段: {extra_fields}")

    print("\n数据格式转换测试完成!")


if __name__ == "__main__":
    test_data_format_conversion()
