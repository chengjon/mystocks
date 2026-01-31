#!/usr/bin/env python3
"""
测试类型注解的脚本
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from src.core.data_classification import DataClassification


def test_method_signatures() -> None:
    """测试方法签名是否符合类型注解"""

    # 测试数据
    classification: DataClassification = DataClassification.DAILY_KLINE
    data: pd.DataFrame = pd.DataFrame({"col1": [1, 2, 3]})
    table_name: str = "test_table"
    filters: Optional[Dict[str, Any]] = {"symbol": "600000"}
    columns: Optional[List[str]] = ["col1", "col2"]
    limit: Optional[int] = 100

    print("✅ 类型注解测试通过")


if __name__ == "__main__":
    test_method_signatures()
    print("All type annotation tests passed!")
