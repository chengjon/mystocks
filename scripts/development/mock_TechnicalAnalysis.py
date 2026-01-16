"""
Mock数据文件: TechnicalAnalysis
提供接口:
1. calculate_indicators() -> Dict - 计算技术指标（对应/indicators/calculate API）
2. get_stock_kline() -> List[Dict] - 获取股票K线数据
3. get_technical_indicators() -> Dict - 获取技术指标数据
4. get_signal_analysis() -> pd.DataFrame - 获取买卖信号分析

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
from typing import Dict


def get_technical_indicators(stock_code: str) -> Dict:
    """获取技术指标数据 - 别名函数，与get_all_indicators相同

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 技术指标数据，包含趋势、动量、波动率、成交量等指标
    """
    return get_all_indicators(stock_code)


def get_all_indicators(stock_code: str) -> Dict:
    """获取所有技术指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 所有技术指标数据，包含趋势、动量、波动率、成交量等指标
    """
    # 生成技术指标数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "trend": {
            "ma5": round(100 + (hash(stock_code) % 20), 2),
            "ma10": round(102 + (hash(stock_code) % 18), 2),
            "ma20": round(104 + (hash(stock_code) % 16), 2),
            "macd": {
                "macd": round(-1 + (hash(stock_code) % 3), 3),
                "signal": round(-0.5 + (hash(stock_code) % 2), 3),
                "hist": round(-0.2 + (hash(stock_code) % 0.5), 3),
            },
        },
        "momentum": {
            "rsi": round(50 + (hash(stock_code) % 40), 2),
            "kdj_k": round(40 + (hash(stock_code) % 40), 2),
            "kdj_d": round(40 + (hash(stock_code) % 40), 2),
            "kdj_j": round(40 + (hash(stock_code) % 40), 2),
        },
        "volatility": {
            "atr": round(2.0 + (hash(stock_code) % 5), 2),
            "bollinger": {
                "upper": round(105 + (hash(stock_code) % 20), 2),
                "middle": round(100 + (hash(stock_code) % 20), 2),
                "lower": round(95 + (hash(stock_code) % 20), 2),
            },
        },
        "volume": {
            "obv": round(1000000 + (hash(stock_code) % 9000000), 0),
            "volume_ma": round(5000000 + (hash(stock_code) % 5000000), 0),
        },
    }

    return result


def get_trend_indicators(stock_code: str) -> Dict:
    """获取趋势指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 趋势指标数据
    """
    # 生成趋势指标数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "trend": {
            "ma5": round(100 + (hash(stock_code) % 20), 2),
            "ma10": round(102 + (hash(stock_code) % 18), 2),
            "ma20": round(104 + (hash(stock_code) % 16), 2),
            "ma30": round(106 + (hash(stock_code) % 14), 2),
            "ma60": round(108 + (hash(stock_code) % 12), 2),
            "ema12": round(101 + (hash(stock_code) % 19), 2),
            "ema26": round(103 + (hash(stock_code) % 17), 2),
            "macd": {
                "macd": round(-1 + (hash(stock_code) % 3), 3),
                "signal": round(-0.5 + (hash(stock_code) % 2), 3),
                "hist": round(-0.2 + (hash(stock_code) % 0.5), 3),
            },
            "bollinger": {
                "upper": round(105 + (hash(stock_code) % 20), 2),
                "middle": round(100 + (hash(stock_code) % 20), 2),
                "lower": round(95 + (hash(stock_code) % 20), 2),
            },
        },
    }

    return result


def get_momentum_indicators(stock_code: str) -> Dict:
    """获取动量指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 动量指标数据
    """
    # 生成动量指标数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "momentum": {
            "rsi": round(50 + (hash(stock_code) % 40), 2),
            "kdj_k": round(40 + (hash(stock_code) % 40), 2),
            "kdj_d": round(40 + (hash(stock_code) % 40), 2),
            "kdj_j": round(40 + (hash(stock_code) % 40), 2),
            "cci": round(-100 + (hash(stock_code) % 200), 2),
            "williams_r": round(-20 + (hash(stock_code) % 60), 2),
        },
    }

    return result


def get_volatility_indicators(stock_code: str) -> Dict:
    """获取波动率指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 波动率指标数据
    """
    # 生成波动率指标数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "volatility": {
            "atr": round(2.0 + (hash(stock_code) % 5), 2),
            "std": round(1.5 + (hash(stock_code) % 3), 2),
            "bollinger": {
                "upper": round(105 + (hash(stock_code) % 20), 2),
                "middle": round(100 + (hash(stock_code) % 20), 2),
                "lower": round(95 + (hash(stock_code) % 20), 2),
            },
            "boll_width": round(0.05 + (hash(stock_code) % 0.1), 3),
            "bbp": round(0.4 + (hash(stock_code) % 0.4), 3),
        },
    }

    return result


def get_volume_indicators(stock_code: str) -> Dict:
    """获取成交量指标

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 成交量指标数据
    """
    # 生成成交量指标数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "volume": {
            "obv": round(1000000 + (hash(stock_code) % 9000000), 0),
            "volume_ma": round(5000000 + (hash(stock_code) % 5000000), 0),
            "volumn_ratio": round(0.8 + (hash(stock_code) % 1.2), 2),
            "vwap": round(98 + (hash(stock_code) % 8), 2),
        },
    }

    return result


def get_trading_signals(stock_code: str) -> Dict:
    """获取交易信号

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 交易信号数据
    """
    # 生成交易信号数据
    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "signals": {
            "signal_type": "买入" if hash(stock_code) % 3 == 0 else ("卖出" if hash(stock_code) % 3 == 1 else "持有"),
            "signal": (
                "MA金叉"
                if hash(stock_code) % 4 == 0
                else ("RSI超卖" if hash(stock_code) % 4 == 1 else "MACD金叉" if hash(stock_code) % 4 == 2 else "无信号")
            ),
            "strength": round(0.6 + (hash(stock_code) % 0.4), 2),
            "confidence": round(0.7 + (hash(stock_code) % 0.3), 2),
            "target_price": round(105 + (hash(stock_code) % 20), 2),
            "stop_loss": round(95 + (hash(stock_code) % 10), 2),
        },
    }

    return result


def get_kline_data(stock_code: str, start_date: str, end_date: str) -> Dict:
    """获取K线历史数据
    Args:
        stock_code: str - 股票代码
        start_date: str - 开始日期 (YYYY-MM-DD)
        end_date: str - 结束日期 (YYYY-MM-DD)
    Returns:
        Dict: K线历史数据
    """
    # 生成K线历史数据
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current_dt = start_dt
    while current_dt <= end_dt:
        dates.append(current_dt.strftime("%Y-%m-%d"))
        current_dt += datetime.timedelta(days=1)

    data = []
    for i in range(len(dates)):
        open_price = round(95 + (hash(stock_code + str(i)) % 10), 2)
        close_price = round(96 + (hash(stock_code + str(i)) % 8), 2)
        high_price = round(98 + (hash(stock_code + str(i)) % 6), 2)
        low_price = round(94 + (hash(stock_code + str(i)) % 6), 2)
        volume = int(1000000 + (hash(stock_code + str(i)) % 9000000))
        data.append(
            {
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
            }
        )

    result = {
        "symbol": stock_code,
        "period": "daily",
        "count": len(dates),
        "dates": dates,
        "data": data,
        "change_percent": [round(-2 + (hash(stock_code + str(i)) % 4), 2) for i in range(len(dates))],
    }

    return result


def calculate_indicators(request: Dict) -> Dict:
    """计算技术指标（对应/indicators/calculate API）

    Args:
        request: Dict - 请求参数，包含 symbol, start_date, end_date, indicators

    Returns:
        Dict: 包含OHLCV数据和计算出的技术指标
    """
    symbol = request.get("symbol")
    start_date = request.get("start_date")
    end_date = request.get("end_date")
    indicators_to_calculate = request.get("indicators", [])

    if not all([symbol, start_date, end_date]):
        return {"error": "Missing required parameters: symbol, start_date, end_date"}

    # 获取K线数据
    kline_data = get_kline_data(symbol, start_date, end_date)

    # 模拟计算指标
    calculated_indicators = {}
    for indicator in indicators_to_calculate:
        if indicator in ["ma5", "ma10", "ma20"]:
            # 模拟均线
            calculated_indicators[indicator] = [
                round(random.uniform(90, 110), 2) for _ in range(len(kline_data["dates"]))
            ]
        elif indicator == "macd":
            calculated_indicators["macd"] = {
                "macd": [round(random.uniform(-5, 5), 3) for _ in range(len(kline_data["dates"]))],
                "signal": [round(random.uniform(-5, 5), 3) for _ in range(len(kline_data["dates"]))],
                "hist": [round(random.uniform(-5, 5), 3) for _ in range(len(kline_data["dates"]))],
            }
        elif indicator == "rsi":
            calculated_indicators["rsi"] = [round(random.uniform(30, 70), 2) for _ in range(len(kline_data["dates"]))]
        # 可以添加更多指标的模拟计算

    return {
        "symbol": symbol,
        "symbol_name": f"Mock_{symbol}",
        "ohlcv": {
            "dates": kline_data["dates"],
            "open": [d["open"] for d in kline_data["data"]],
            "high": [d["high"] for d in kline_data["data"]],
            "low": [d["low"] for d in kline_data["data"]],
            "close": [d["close"] for d in kline_data["data"]],
            "volume": [d["volume"] for d in kline_data["data"]],
        },
        "indicators": calculated_indicators,
    }


def get_pattern_recognition(stock_code: str) -> Dict:
    """获取形态识别结果

    Args:
        stock_code: str - 股票代码

    Returns:
        Dict: 形态识别结果
    """
    # 生成形态识别数据
    patterns = [
        "头肩底",
        "双底",
        "三重顶",
        "上升三角形",
        "下降三角形",
        "矩形整理",
        "楔形",
        "旗形",
    ]

    result = {
        "symbol": stock_code,
        "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "patterns": [
            {
                "pattern_name": random.choice(patterns),
                "confidence": round(0.7 + (hash(stock_code + str(i)) % 0.3), 2),
                "target_price": round(105 + (hash(stock_code + str(i)) % 20), 2),
                "stop_loss": round(95 + (hash(stock_code + str(i)) % 10), 2),
                "signal": (
                    "买入"
                    if hash(stock_code + str(i)) % 3 == 0
                    else ("卖出" if hash(stock_code + str(i)) % 3 == 1 else "持有")
                ),
            }
            for i in range(3)
        ],
    }

    return result


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
    print("get_all_indicators() 调用测试:")
    result1 = get_all_indicators("600000")
    print(f"返回数据: {result1}")

    print("\nget_trend_indicators() 调用测试:")
    result2 = get_trend_indicators("600000")
    print(f"返回数据: {result2}")

    print("\nget_momentum_indicators() 调用测试:")
    result3 = get_momentum_indicators("600000")
    print(f"返回数据: {result3}")
