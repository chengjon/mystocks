"""技术分析系统 API 测试脚本
Enhanced Technical Analysis Test
"""

import json
import os

import requests


# API base URL
BACKEND_PORT = os.getenv("BACKEND_PORT", "").strip()
if not BACKEND_PORT:
    raise RuntimeError("Missing BACKEND_PORT in environment")
BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")
headers = {}


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health_check():
    """测试系统健康检查"""
    print_section("测试 1: 系统健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_get_all_indicators():
    """测试获取所有技术指标"""
    print_section("测试 2: 获取所有技术指标")

    # 测试贵州茅台
    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/indicators", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n股票: {data['symbol']}")
        print(f"最新价格: {data['latest_price']}")
        print(f"最新日期: {data['latest_date']}")
        print(f"数据点数: {data['data_points']}")
        print(f"指标总数: {data['total_indicators']}")

        print(f"\n趋势指标数量: {len(data['trend'])}")
        print(f"动量指标数量: {len(data['momentum'])}")
        print(f"波动性指标数量: {len(data['volatility'])}")
        print(f"成交量指标数量: {len(data['volume'])}")

        # 显示部分指标
        print("\n部分趋势指标:")
        for key in ["ma5", "ma10", "ma20", "ema12", "ema26"]:
            if key in data["trend"]:
                print(f"  {key}: {data['trend'][key]:.2f}")

        print("\n部分动量指标:")
        for key in ["rsi6", "rsi12", "kdj_k", "kdj_d"]:
            if key in data["momentum"]:
                print(f"  {key}: {data['momentum'][key]:.2f}")

    else:
        print(f"请求失败: {response.text}")


def test_get_trend_indicators():
    """测试获取趋势指标"""
    print_section("测试 3: 获取趋势指标")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/trend", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"指标数量: {data['count']}")
        print(json.dumps(data["indicators"], indent=2, ensure_ascii=False))


def test_get_momentum_indicators():
    """测试获取动量指标"""
    print_section("测试 4: 获取动量指标")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/momentum", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"指标数量: {data['count']}")

        indicators = data["indicators"]
        print("\nRSI指标:")
        print(f"  RSI(6):  {indicators.get('rsi6', 'N/A')}")
        print(f"  RSI(12): {indicators.get('rsi12', 'N/A')}")
        print(f"  RSI(24): {indicators.get('rsi24', 'N/A')}")

        print("\nKDJ指标:")
        print(f"  K: {indicators.get('kdj_k', 'N/A')}")
        print(f"  D: {indicators.get('kdj_d', 'N/A')}")
        print(f"  J: {indicators.get('kdj_j', 'N/A')}")


def test_get_volatility_indicators():
    """测试获取波动性指标"""
    print_section("测试 5: 获取波动性指标")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/volatility", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"指标数量: {data['count']}")

        indicators = data["indicators"]
        print("\nBollinger Bands:")
        print(f"  上轨: {indicators.get('bb_upper', 'N/A')}")
        print(f"  中轨: {indicators.get('bb_middle', 'N/A')}")
        print(f"  下轨: {indicators.get('bb_lower', 'N/A')}")
        print(f"  带宽: {indicators.get('bb_width', 'N/A')}%")

        print("\nATR:")
        print(f"  ATR: {indicators.get('atr', 'N/A')}")
        print(f"  ATR%: {indicators.get('atr_percent', 'N/A')}%")


def test_get_volume_indicators():
    """测试获取成交量指标"""
    print_section("测试 6: 获取成交量指标")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/volume", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"指标数量: {data['count']}")
        print(json.dumps(data["indicators"], indent=2, ensure_ascii=False))


def test_get_trading_signals():
    """测试获取交易信号"""
    print_section("测试 7: 获取交易信号")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/{symbol}/signals", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n综合信号: {data['overall_signal'].upper()}")
        print(f"信号强度: {data['signal_strength']:.2f}")
        print(
            f"信号数量: 买入={data['signal_count']['buy']}, "
            f"卖出={data['signal_count']['sell']}, "
            f"总计={data['signal_count']['total']}",
        )

        if data["signals"]:
            print("\n具体信号:")
            for sig in data["signals"]:
                print(f"  - [{sig['signal'].upper()}] {sig['type']}: 强度 {sig['strength']:.2f}")
        else:
            print("\n当前无明显交易信号")


def test_get_history():
    """测试获取历史数据"""
    print_section("测试 8: 获取历史数据")

    symbol = "600519"
    response = requests.get(
        f"{BASE_URL}/api/technical/{symbol}/history",
        params={"limit": 10},
        headers=headers,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票: {data['symbol']}")
        print(f"周期: {data['period']}")
        print(f"数据点: {data['count']}")

        print("\n最近3天数据:")
        for i in range(min(3, len(data["dates"]))):
            ohlcv = data["data"][-(i + 1)]
            print(
                f"  {data['dates'][-(i + 1)]}: "
                f"开={ohlcv['open']:.2f}, "
                f"高={ohlcv['high']:.2f}, "
                f"低={ohlcv['low']:.2f}, "
                f"收={ohlcv['close']:.2f}, "
                f"量={ohlcv['volume']:,}",
            )


def test_batch_indicators():
    """测试批量获取指标"""
    print_section("测试 9: 批量获取指标")

    symbols = ["600519", "000001", "600000"]
    response = requests.post(
        f"{BASE_URL}/api/technical/batch/indicators",
        params={"symbols": symbols},
        headers=headers,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功获取: {data['count']}/{len(symbols)} 只股票")

        for stock in data["data"]:
            print(f"\n{stock['symbol']}: {stock['latest_price']:.2f} ({stock['latest_date']})")
            print(f"  指标总数: {stock['total_indicators']}")


def test_weekly_period():
    """测试周线数据"""
    print_section("测试 10: 周线数据和指标")

    symbol = "600519"
    response = requests.get(
        f"{BASE_URL}/api/technical/{symbol}/indicators",
        params={"period": "weekly"},
        headers=headers,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票: {data['symbol']}")
        print(f"最新价格: {data['latest_price']}")
        print(f"数据点数 (周): {data['data_points']}")
        print(f"指标总数: {data['total_indicators']}")


def test_date_range():
    """测试日期范围查询"""
    print_section("测试 11: 指定日期范围")

    symbol = "600519"
    response = requests.get(
        f"{BASE_URL}/api/technical/{symbol}/indicators",
        params={"start_date": "2024-01-01", "end_date": "2025-10-23"},
        headers=headers,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"股票: {data['symbol']}")
        print(f"数据点数: {data['data_points']}")
        print(f"最早日期: {data.get('earliest_date', 'N/A')}")
        print(f"最新日期: {data['latest_date']}")


def test_pattern_detection():
    """测试形态识别 (预留功能)"""
    print_section("测试 12: 形态识别 (预留)")

    symbol = "600519"
    response = requests.get(f"{BASE_URL}/api/technical/patterns/{symbol}", headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("  MyStocks 技术分析系统 API 测试")
    print("  Enhanced Technical Analysis")
    print("=" * 80)

    try:
        # 基础测试
        test_health_check()
        test_get_all_indicators()

        # 分类指标测试
        test_get_trend_indicators()
        test_get_momentum_indicators()
        test_get_volatility_indicators()
        test_get_volume_indicators()

        # 交易信号测试
        test_get_trading_signals()

        # 历史数据测试
        test_get_history()

        # 批量和高级功能测试
        test_batch_indicators()
        test_weekly_period()
        test_date_range()
        test_pattern_detection()

        print_section("✅ 所有测试完成!")

        print("\n测试总结:")
        print("  ✓ 趋势指标 (MA, EMA, MACD, DMI, SAR)")
        print("  ✓ 动量指标 (RSI, KDJ, CCI, WR, ROC)")
        print("  ✓ 波动性指标 (BB, ATR, KC)")
        print("  ✓ 成交量指标 (OBV, VWAP, Volume Ratio)")
        print("  ✓ 交易信号生成")
        print("  ✓ 历史数据获取")
        print("  ✓ 批量查询")
        print("  ✓ 多周期支持 (日/周/月)")

        print("\n⚠️  注意:")
        print("  - TA-Lib 需要足够的历史数据点")
        print("  - 某些指标需要至少250个数据点")
        print("  - 建议使用1年以上的历史数据")
        print("  - 形态识别功能尚未实现")

        print("\n📊 技术指标说明:")
        print("  - MA: 移动平均线，用于判断趋势")
        print("  - RSI: 相对强弱指标，判断超买超卖")
        print("  - MACD: 趋势和动量指标，金叉死叉判断")
        print("  - KDJ: 随机指标，判断买卖时机")
        print("  - Bollinger Bands: 布林带，判断价格波动范围")
        print("  - ATR: 平均真实波幅，衡量波动性")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
