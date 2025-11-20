"""
MyStocks项目测试配置文件
提供测试夹具、mock数据和通用测试设置
"""

import pytest
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# from unittest.mock import Mock, MagicMock
# import sys
# import os
# from pathlib import Path

# # 确保能够导入项目模块
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))


# @pytest.fixture(scope="session")
# def test_data_dir():
#     """测试数据目录夹具"""
#     return project_root / "tests" / "data"


# @pytest.fixture(scope="session")
# def sample_stock_data():
#     """示例股票数据夹具"""
#     dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
#     data = []
#     for i, date in enumerate(dates):
#         data.append({
#             'date': date,
#             'open': 10.0 + i * 0.1,
#             'high': 10.5 + i * 0.1,
#             'low': 9.5 + i * 0.1,
#             'close': 10.2 + i * 0.1,
#             'volume': 1000000 + i * 1000,
#             'amount': 10000000 + i * 100000,
#             'pct_chg': (i * 0.1),
#             'symbol': '000001'
#         })
    
#     return pd.DataFrame(data)


def test_minimal():
    """最小测试函数"""
    assert True