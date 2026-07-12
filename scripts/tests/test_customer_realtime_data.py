#!/usr/bin/env python3
"""测试Customer适配器获取实时数据的脚本
用于了解stock.get_realtime_quotes()返回的数据结构
"""

import os
import sys


# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pandas as pd

from src.adapters.customer_adapter import CustomerDataSource


def test_realtime_data_structure():
    """测试获取实时数据的结构"""
    print("=== 测试Customer适配器获取实时数据 ===")

    # 创建适配器
    customer_ds = CustomerDataSource()

    if not customer_ds.efinance_available:
        print("❌ efinance不可用，无法测试")
        return None

    try:
        # 获取沪深市场A股最新状况
        print("正在获取沪深市场A股最新状况...")
        data = customer_ds.get_real_time_data("hs")  # 沪深市场

        if isinstance(data, pd.DataFrame) and not data.empty:
            print(f"✅ 成功获取数据，共 {len(data)} 行")
            print(f"📊 数据列名: {list(data.columns)}")
            print(f"📈 数据类型:\n{data.dtypes}")
            print(f"📝 前5行数据:\n{data.head()}")
            print(f"🔍 数据示例:\n{data.iloc[0].to_dict()}")

            return data
        print("❌ 未获取到有效数据")
        return None

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None


if __name__ == "__main__":
    data = test_realtime_data_structure()
