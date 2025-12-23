#!/usr/bin/env python3
"""
批量生成Mock文件模板脚本
基于页面清单自动生成25个Mock文件模板

生成时间: 2025-11-13
"""

import os
from typing import List, Dict

# Mock文件存放目录
MOCK_DIR = "/opt/claude/mystocks_spec/src/mock"
os.makedirs(MOCK_DIR, exist_ok=True)

# 25个Mock文件清单（与行动计划一致）
mock_files: List[str] = [
    # 核心业务页面（16个）
    "mock_Dashboard.py",
    "mock_Market.py",
    "mock_MarketData.py",
    "mock_Stocks.py",
    "mock_TechnicalAnalysis.py",
    "mock_Wencai.py",
    "mock_StrategyManagement.py",
    "mock_TaskManagement.py",
    "mock_RealTimeMonitor.py",
    "mock_Analysis.py",
    "mock_RiskMonitor.py",
    "mock_TradeManagement.py",
    "mock_IndicatorLibrary.py",
    "mock_BacktestAnalysis.py",
    "mock_TdxMarket.py",
    "mock_Settings.py",
    # 辅助功能页面（1个）
    "mock_Login.py",
    # 策略管理子模块（5个）
    "mock_strategy_BatchScan.py",
    "mock_strategy_ResultsQuery.py",
    "mock_strategy_StatsAnalysis.py",
    "mock_strategy_StrategyList.py",
    "mock_strategy_SingleRun.py",
    # 系统监控子模块（2个）
    "mock_system_Architecture.py",
    "mock_system_DatabaseMonitor.py",
    # 市场数据视图（1个）
    "mock_MarketDataView.py",
]

# 核心页面的函数映射（已明确接口的页面）
page_func_mapping: Dict[str, Dict[str, str]] = {
    "mock_Stocks.py": {
        "func1": "stock_list",
        "func2": "real_time_quote",
        "func3": "history_profit",
        "desc1": "获取股票列表（支持按交易所筛选）",
        "desc2": "获取实时行情（必填参数：股票代码）",
        "desc3": "获取历史收益（默认30天，返回DataFrame）",
    },
    "mock_Dashboard.py": {
        "func1": "market_hot",
        "func2": "plate_performance",
        "func3": "fund_flow",
        "desc1": "获取市场热度数据",
        "desc2": "获取板块表现数据",
        "desc3": "获取资金流向统计",
    },
    "mock_TechnicalAnalysis.py": {
        "func1": "stock_kline",
        "func2": "technical_indicators",
        "func3": "signal_analysis",
        "desc1": "获取股票K线数据",
        "desc2": "获取技术指标数据",
        "desc3": "获取买卖信号分析",
    },
    "mock_Wencai.py": {
        "func1": "wencai_queries",
        "func2": "query_results",
        "func3": "custom_query",
        "desc1": "获取预定义查询列表",
        "desc2": "获取查询结果数据",
        "desc3": "执行自定义问财查询",
    },
}

# 通用模板内容
template_content = '''"""
Mock数据文件: {page_name}
提供接口:
1. get_{func1}() -> List[Dict] - {desc1}
2. get_{func2}() -> Dict - {desc2}
3. get_{func3}() -> pd.DataFrame - {desc3}

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import List, Dict, Optional
import pandas as pd
import datetime
import random
from decimal import Decimal


# TODO: 根据实际API接口修改函数实现
def get_{func1}({func1_params}) -> List[Dict]:
    """{desc1}

    Args:
        {func1_args_docs}

    Returns:
        List[Dict]: {desc1}数据列表
    """
    # TODO: 实现具体的数据生成逻辑
    # 示例Mock数据
    mock_data = [
        {{
            "id": 1,
            "name": "示例数据",
            "value": 100.0,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }}
    ]
    return mock_data


def get_{func2}({func2_params}) -> Dict:
    """{desc2}

    Args:
        {func2_args_docs}

    Returns:
        Dict: {desc2}数据
    """
    # TODO: 实现具体的数据生成逻辑
    mock_data = {{
        "id": 1,
        "name": "示例数据",
        "value": 100.0,
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }}
    return mock_data


def get_{func3}({func3_params}) -> pd.DataFrame:
    """{desc3}

    Args:
        {func3_args_docs}

    Returns:
        pd.DataFrame: {desc3}数据表格，列名对应前端表格字段
    """
    # TODO: 实现具体的数据生成逻辑
    # 示例DataFrame数据
    data = {{
        "date": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "value": [100.0, 101.0, 99.5],
        "change_rate": [0.0, 0.01, -0.015]
    }}
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
    print(f"get_{func1}() 调用测试:")
    result1 = get_{func1}({func1_test_args})
    print(f"返回数据: {{result1}}")

    print(f"\nget_{func2}() 调用测试:")
    result2 = get_{func2}({func2_test_args})
    print(f"返回数据: {{result2}}")

    print(f"\nget_{func3}() 调用测试:")
    result3 = get_{func3}({func3_test_args})
    print(f"返回数据:\n{{result3}}")
'''


def generate_function_params_and_docs(params_str: str) -> tuple[str, str]:
    """生成函数参数和文档字符串"""
    if not params_str:
        return "", ""

    # 解析参数
    params = [p.strip() for p in params_str.split(",")]
    param_str = ", ".join(params)
    args_docs = "\n        ".join(
        [
            f"{p.split(':')[0].strip()}: {p.split(':')[1].strip() if ':' in p else 'str'} - 参数说明"
            for p in params
        ]
    )

    return param_str, args_docs


def main():
    """主函数：批量生成Mock文件"""
    print("🚀 开始批量生成Mock文件模板")
    print("=" * 60)

    success_count = 0

    for file_name in mock_files:
        try:
            page_name = file_name.replace("mock_", "").replace(".py", "")

            # 获取页面函数映射（使用默认值）
            func_mapping = page_func_mapping.get(
                file_name,
                {
                    "func1": "data_list",
                    "func2": "data_detail",
                    "func3": "data_table",
                    "desc1": "获取数据列表",
                    "desc2": "获取数据详情",
                    "desc3": "获取数据表格",
                },
            )

            # 生成参数和文档
            func1_params = ""
            func2_params = ""
            func3_params = ""
            func1_args_docs = ""
            func2_args_docs = ""
            func3_args_docs = ""

            # 为特殊页面添加默认参数
            if "Stocks" in page_name:
                func1_params = "exchange: Optional[str] = None"
                func2_params = "code: str"
                func3_params = "code: str, days: int = 30"
                func1_args_docs = (
                    "exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）"
                )
                func2_args_docs = "code: str - 股票代码（必填）"
                func3_args_docs = "code: str - 股票代码（必填）\n        days: int - 历史天数，默认30天"

                func1_test_args = "exchange='sh'"
                func2_test_args = "code='600000'"
                func3_test_args = "code='600000', days=30"

            elif "Dashboard" in page_name:
                func1_test_args = ""
                func2_test_args = ""
                func3_test_args = ""

            else:
                func1_test_args = ""
                func2_test_args = ""
                func3_test_args = ""

            # 填充模板
            content = template_content.format(
                page_name=page_name,
                func1=func_mapping["func1"],
                func2=func_mapping["func2"],
                func3=func_mapping["func3"],
                desc1=func_mapping["desc1"],
                desc2=func_mapping["desc2"],
                desc3=func_mapping["desc3"],
                func1_params=func1_params,
                func2_params=func2_params,
                func3_params=func3_params,
                func1_args_docs=func1_args_docs,
                func2_args_docs=func2_args_docs,
                func3_args_docs=func3_args_docs,
                func1_test_args=func1_test_args,
                func2_test_args=func2_test_args,
                func3_test_args=func3_test_args,
            )

            # 写入文件
            file_path = os.path.join(MOCK_DIR, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            success_count += 1
            print(f"✅ {file_name} - 生成成功")

        except Exception as e:
            print(f"❌ {file_name} - 生成失败: {e}")

    print("=" * 60)
    print(f"🎯 生成完成！成功: {success_count}/{len(mock_files)} 个文件")

    if success_count == len(mock_files):
        print("🚀 所有Mock文件模板生成成功！")
        print(f"📁 文件存放位置: {MOCK_DIR}")
        print("📋 下一步：开始实施核心页面的Mock数据实现")
    else:
        print("⚠️  部分文件生成失败，请检查错误信息")


if __name__ == "__main__":
    main()
