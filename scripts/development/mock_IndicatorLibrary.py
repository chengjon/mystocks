"""
Mock数据文件: IndicatorLibrary
提供接口:
1. get_indicator_list() -> List[Dict] - 获取指标列表
2. get_indicator_detail() -> Dict - 获取指标详情
3. get_indicator_data() -> pd.DataFrame - 获取指标数据表格

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-15
"""

from typing import List, Dict, Optional
import pandas as pd
import datetime
import random


def get_indicator_list(params: Optional[Dict] = None) -> List[Dict]:
    """获取指标列表

    Args:
        params: Dict - 查询参数：
                category: Optional[str] - 指标分类（trend, momentum, volatility, volume）
                limit: int - 每页数量，默认20
                offset: int - 偏移量，默认0

    Returns:
        List[Dict]: 指标列表数据，前端表格所需字段：
                   - id: 指标ID
                   - name: 指标名称
                   - category: 指标分类
                   - description: 指标描述
                   - formula: 计算公式
                   - created_at: 创建时间
    """
    # 默认参数
    params = params or {}
    category = params.get("category")
    limit = params.get("limit", 20)
    offset = params.get("offset", 0)

    # 指标基础数据池（包含各种技术指标）
    indicator_pools = {
        "trend": [
            {
                "id": "ma5",
                "name": "5日移动平均线",
                "category": "trend",
                "description": "5日收盘价移动平均线",
                "formula": "MA(CLOSE, 5)",
            },
            {
                "id": "ma10",
                "name": "10日移动平均线",
                "category": "trend",
                "description": "10日收盘价移动平均线",
                "formula": "MA(CLOSE, 10)",
            },
            {
                "id": "ma20",
                "name": "20日移动平均线",
                "category": "trend",
                "description": "20日收盘价移动平均线",
                "formula": "MA(CLOSE, 20)",
            },
            {
                "id": "ema12",
                "name": "12日指数移动平均线",
                "category": "trend",
                "description": "12日收盘价指数移动平均线",
                "formula": "EMA(CLOSE, 12)",
            },
            {
                "id": "ema26",
                "name": "26日指数移动平均线",
                "category": "trend",
                "description": "26日收盘价指数移动平均线",
                "formula": "EMA(CLOSE, 26)",
            },
            {
                "id": "macd",
                "name": "MACD",
                "category": "trend",
                "description": "指数平滑异同移动平均线",
                "formula": "DIF, DEA, BAR",
            },
            {
                "id": "bollinger",
                "name": "布林带",
                "category": "trend",
                "description": "布林带指标",
                "formula": "UPPER, MIDDLE, LOWER",
            },
        ],
        "momentum": [
            {
                "id": "rsi",
                "name": "相对强弱指标",
                "category": "momentum",
                "description": "相对强弱指数",
                "formula": "RSI(CLOSE, 14)",
            },
            {
                "id": "kdj_k",
                "name": "KDJ_K线",
                "category": "momentum",
                "description": "随机指标K线",
                "formula": "KDJ(K, D, J)",
            },
            {
                "id": "kdj_d",
                "name": "KDJ_D线",
                "category": "momentum",
                "description": "随机指标D线",
                "formula": "KDJ(K, D, J)",
            },
            {
                "id": "kdj_j",
                "name": "KDJ_J线",
                "category": "momentum",
                "description": "随机指标J线",
                "formula": "KDJ(K, D, J)",
            },
            {
                "id": "cci",
                "name": "商品通道指数",
                "category": "momentum",
                "description": "商品通道指数",
                "formula": "CCI(HIGH, LOW, CLOSE, 14)",
            },
            {
                "id": "williams",
                "name": "威廉指标",
                "category": "momentum",
                "description": "威廉指标",
                "formula": "WR(HIGH, LOW, CLOSE, 14)",
            },
        ],
        "volatility": [
            {
                "id": "atr",
                "name": "平均真实波幅",
                "category": "volatility",
                "description": "平均真实波幅",
                "formula": "ATR(HIGH, LOW, CLOSE, 14)",
            },
            {
                "id": "std",
                "name": "标准差",
                "category": "volatility",
                "description": "收盘价标准差",
                "formula": "STD(CLOSE, 10)",
            },
            {
                "id": "boll_width",
                "name": "布林带宽度",
                "category": "volatility",
                "description": "布林带宽度",
                "formula": "BOLL_WIDTH",
            },
            {
                "id": "bbp",
                "name": "布林带位置",
                "category": "volatility",
                "description": "布林带位置",
                "formula": "BBP(CLOSE, UPPER, LOWER)",
            },
        ],
        "volume": [
            {
                "id": "obv",
                "name": "能量潮",
                "category": "volume",
                "description": "能量潮指标",
                "formula": "OBV(CLOSE, VOLUME)",
            },
            {
                "id": "volumn_ma",
                "name": "成交量移动平均",
                "category": "volume",
                "description": "成交量移动平均线",
                "formula": "MA(VOLUME, 5)",
            },
            {
                "id": "volumn_ratio",
                "name": "量比",
                "category": "volume",
                "description": "量比指标",
                "formula": "VOLUME_RATIO",
            },
            {
                "id": "vwap",
                "name": "成交量加权平均价",
                "category": "volume",
                "description": "成交量加权平均价",
                "formula": "VWAP",
            },
        ],
    }

    # 根据分类筛选
    if category:
        available_indicators = indicator_pools.get(category, [])
    else:
        available_indicators = []
        for indicators in indicator_pools.values():
            available_indicators.extend(indicators)

    # 生成分页数据
    total_indicators = len(available_indicators)
    paginated_indicators = available_indicators[offset : offset + limit]

    # 为每个指标生成创建日期和实际数据
    result = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=365)  # 约1年前的日期

    for i, indicator in enumerate(paginated_indicators):
        created_date = base_date + datetime.timedelta(days=random.randint(0, 365))
        result.append(
            {
                "id": indicator["id"],
                "name": indicator["name"],
                "category": indicator["category"],
                "description": indicator["description"],
                "formula": indicator["formula"],
                "created_at": created_date.strftime("%Y-%m-%d %H:%M:%S"),
                "total": total_indicators,  # 用于分页的总数量
            }
        )

    return result


def get_indicator_detail(indicator_id: str) -> Dict:
    """获取指标详情

    Args:
        indicator_id: str - 指标ID

    Returns:
        Dict: 指标详情数据，包含：
             - id: 指标ID
             - name: 指标名称
             - category: 指标分类
             - description: 指标描述
             - formula: 计算公式
             - parameters: 参数列表
             - usage: 使用说明
             - interpretation: 指标解读
    """
    # 指标详细信息
    indicator_details = {
        "ma5": {
            "name": "5日移动平均线",
            "category": "trend",
            "description": "5日收盘价移动平均线，反映短期价格趋势",
            "formula": "MA(CLOSE, 5)",
            "parameters": ["period: 5"],
            "usage": "短期趋势跟踪",
            "interpretation": "价格在均线上方为多头趋势，下方为空头趋势",
        },
        "rsi": {
            "name": "相对强弱指标",
            "category": "momentum",
            "description": "衡量价格变动速度和幅度的振荡器",
            "formula": "RSI(CLOSE, 14)",
            "parameters": ["lookback_period: 14"],
            "usage": "判断超买超卖",
            "interpretation": "RSI > 70 为超买，RSI < 30 为超卖",
        },
        "macd": {
            "name": "MACD",
            "category": "trend",
            "description": "指数平滑异同移动平均线，用于识别趋势变化",
            "formula": "DIF=EMA(CLOSE,12)-EMA(CLOSE,26); DEA=EMA(DIF,9); BAR=2*(DIF-DEA)",
            "parameters": ["fast_period: 12", "slow_period: 26", "signal_period: 9"],
            "usage": "趋势识别和背离分析",
            "interpretation": "DIF上穿DEA为买入信号，下穿为卖出信号",
        },
        "kdj_k": {
            "name": "KDJ_K线",
            "category": "momentum",
            "description": "随机指标K线，反映价格在周期内相对位置",
            "formula": "RSV=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100; K=SMA(RSV,M1,1); D=SMA(K,M2,1); J=3*K-2*D",
            "parameters": ["n_period: 9", "k_period: 3", "d_period: 3"],
            "usage": "判断超买超卖和趋势反转",
            "interpretation": "K > 80 为超买，K < 20 为超卖",
        },
        "atr": {
            "name": "平均真实波幅",
            "category": "volatility",
            "description": "衡量价格波动性的指标",
            "formula": "ATR(MAX(MAX(HIGH-LOW, ABS(HIGH-REF(CLOSE,1))), ABS(LOW-REF(CLOSE,1))), N)",
            "parameters": ["period: 14"],
            "usage": "设置止损位和评估波动性",
            "interpretation": "ATR值越大，波动性越大",
        },
        "obv": {
            "name": "能量潮",
            "category": "volume",
            "description": "通过成交量变化来预测价格趋势",
            "formula": "IF(CLOSE>REF(CLOSE,1), VOLUME, IF(CLOSE<REF(CLOSE,1), -VOLUME, 0)); OBV=CUM(SUMVOL)",
            "parameters": ["none"],
            "usage": "确认价格趋势和预测反转",
            "interpretation": "OBV上升配合价格上升，趋势有效；否则可能反转",
        },
    }

    # 获取基础信息
    detail = indicator_details.get(
        indicator_id,
        {
            "name": f"指标{indicator_id}",
            "category": "unknown",
            "description": "未知指标",
            "formula": "未知公式",
            "parameters": ["unknown"],
            "usage": "未知用途",
            "interpretation": "未知解读",
        },
    )

    return {
        "id": indicator_id,
        "name": detail["name"],
        "category": detail["category"],
        "description": detail["description"],
        "formula": detail["formula"],
        "parameters": detail["parameters"],
        "usage": detail["usage"],
        "interpretation": detail["interpretation"],
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_indicator_data(indicator_id: str, symbol: str, days: int = 30) -> pd.DataFrame:
    """获取指标数据表格

    Args:
        indicator_id: str - 指标ID
        symbol: str - 股票代码
        days: int - 历史天数，默认30天

    Returns:
        pd.DataFrame: 指标数据表格，列名对应前端表格字段
    """
    # 股票基础价格
    base_prices = {
        "600519": 1800.0,
        "600036": 35.0,
        "000001": 12.0,
        "000002": 8.5,
        "000858": 150.0,
        "600276": 45.0,
        "600000": 8.0,
        "600887": 28.0,
    }

    base_price = base_prices.get(symbol, 100.0)

    # 生成历史数据
    dates = []
    indicator_values = []

    current_price = base_price
    end_date = datetime.datetime.now()

    for i in range(days):
        date = end_date - datetime.timedelta(days=days - 1 - i)

        # 跳过周末（简化处理）
        if date.weekday() >= 5:
            continue

        dates.append(date.strftime("%Y-%m-%d"))

        # 根据指标类型生成相应的数据
        if indicator_id in ["ma5", "ma10", "ma20", "ema12", "ema26"]:
            # 移动平均线类型指标，返回价格附近值
            indicator_value = round(current_price + random.uniform(-5.0, 5.0), 2)
        elif indicator_id == "rsi":
            # RSI指标，范围0-100
            indicator_value = round(random.uniform(20.0, 80.0), 2)
        elif indicator_id == "kdj_k":
            # KDJ_K指标，范围0-100
            indicator_value = round(random.uniform(20.0, 80.0), 2)
        elif indicator_id == "kdj_d":
            # KDJ_D指标，范围0-100
            indicator_value = round(random.uniform(20.0, 80.0), 2)
        elif indicator_id == "kdj_j":
            # KDJ_J指标，范围0-100
            indicator_value = round(random.uniform(20.0, 80.0), 2)
        elif indicator_id == "macd":
            # MACD指标，可正可负
            indicator_value = round(random.uniform(-2.0, 2.0), 4)
        elif indicator_id == "atr":
            # ATR指标，正值
            indicator_value = round(random.uniform(0.5, 5.0), 2)
        elif indicator_id == "obv":
            # OBV指标，累积成交量
            indicator_value = round(random.uniform(1000000, 100000000), 0)
        elif indicator_id == "bollinger":
            # 布林带，返回中轨值
            indicator_value = round(current_price, 2)
        elif indicator_id == "std":
            # 标准差
            indicator_value = round(random.uniform(0.5, 5.0), 2)
        else:
            # 其他指标，生成合理范围的值
            indicator_value = round(random.uniform(0.0, 100.0), 2)

        indicator_values.append(indicator_value)

        # 模拟价格小幅变动
        change = round(random.uniform(-3.0, 3.0), 2)
        current_price = round(current_price + change, 2)

    # 根据指标类型确定列名
    if indicator_id.startswith("kdj"):
        column_names = {"kdj_k": "kdj_k", "kdj_d": "kdj_d", "kdj_j": "kdj_j"}
        column_name = column_names.get(indicator_id, "value")
    else:
        column_name = indicator_id

    return pd.DataFrame(
        {
            "date": dates,
            column_name: indicator_values,
        }
    )


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
    print("get_indicator_list() 调用测试:")
    result1 = get_indicator_list()
    print(f"返回数据: {result1}")

    print("\nget_indicator_detail() 调用测试:")
    result2 = get_indicator_detail("rsi")
    print(f"返回数据: {result2}")

    print("\nget_indicator_data() 调用测试:")
    result3 = get_indicator_data("rsi", "600000", 30)
    print(f"返回数据:\n{result3}")
