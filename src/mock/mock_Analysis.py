"""
Mock数据文件: Analysis
提供接口:
1. get_data_list() -> List[Dict] - 获取数据列表
2. get_data_detail() -> Dict - 获取数据详情
3. get_data_table() -> pd.DataFrame - 获取数据表格

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

import datetime
import random
from typing import Dict, List

import pandas as pd


def get_data_list() -> List[Dict]:
    """获取数据列表

    Args:


    Returns:
        List[Dict]: 获取数据列表数据列表
    """

    # 示例Mock数据
    mock_data = [
        {
            "id": 1,
            "name": "示例数据",
            "value": 100.0,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    ]
    return mock_data


def get_data_detail() -> Dict:
    """获取数据详情

    Args:


    Returns:
        Dict: 获取数据详情数据
    """

    mock_data = {
        "id": 1,
        "name": "示例数据",
        "value": 100.0,
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return mock_data


def get_data_table() -> pd.DataFrame:
    """获取数据表格

    Args:


    Returns:
        pd.DataFrame: 获取数据表格数据表格，列名对应前端表格字段
    """

    # 示例DataFrame数据
    data = {
        "date": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "value": [100.0, 101.0, 99.5],
        "change_rate": [0.0, 0.01, -0.015],
    }
    return pd.DataFrame(data)


def generate_realistic_price(base_price: float = 100.0, volatility: float = 0.02) -> float:
    """生成真实感的价格数据

    Args:
        base_price: 基准价格
        volatility: 波动率

    Returns:
        float: 生成的价格（保留2位小数）
    """
    change_rate = random.uniform(-volatility, volatility)
    price = base_price * (1 + change_rate)
    return round(price, 2)


def generate_realistic_volume() -> int:
    """生成真实感的成交量数据

    Returns:
        int: 成交量（股）
    """
    return random.randint(1000000, 100000000)


if __name__ == "__main__":
    # 测试函数
    print("Mock文件模板测试")
    print("=" * 50)
    print("get_data_list() 调用测试:")
    result1 = get_data_list()
    print(f"返回数据: {result1}")

    print("get_data_detail() 调用测试:")
    result2 = get_data_detail()
    print(f"返回数据: {result2}")

    print("get_data_table() 调用测试:")
    result3 = get_data_table()
    print(f"返回数据:\n{result3}")
