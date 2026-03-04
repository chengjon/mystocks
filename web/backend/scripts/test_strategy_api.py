#!/usr/bin/env python3
"""
测试股票策略系统API端点
测试10个股票策略的各项功能
"""

import requests
import json
import os

BACKEND_PORT = os.getenv("BACKEND_PORT", "").strip()
if not BACKEND_PORT:
    raise RuntimeError("Missing BACKEND_PORT in environment")
BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")


def print_response(response, title="响应"):
    """打印响应结果"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_get_strategy_definitions():
    """测试1: 获取所有策略定义"""
    print("\n🧪 测试1: 获取所有策略定义")
    url = f"{BASE_URL}/api/strategy/definitions"
    response = requests.get(url)
    print_response(response, "策略定义列表")
    return response.status_code == 200


def test_run_single_strategy():
    """测试2: 对单只股票运行策略（贵州茅台 - 海龟交易法则）"""
    print("\n🧪 测试2: 对单只股票运行策略")
    url = f"{BASE_URL}/api/strategy/run/single"
    params = {
        "strategy_code": "turtle_trading",
        "symbol": "600519",
        "stock_name": "贵州茅台",
    }
    response = requests.post(url, params=params)
    print_response(response, "单只股票策略运行结果")
    return response.status_code == 200


def test_run_single_strategy_volume_surge():
    """测试3: 对单只股票运行策略（平安银行 - 放量上涨）"""
    print("\n🧪 测试3: 对单只股票运行策略（放量上涨）")
    url = f"{BASE_URL}/api/strategy/run/single"
    params = {
        "strategy_code": "volume_surge",
        "symbol": "000001",
        "stock_name": "平安银行",
    }
    response = requests.post(url, params=params)
    print_response(response, "放量上涨策略运行结果")
    return response.status_code == 200


def test_run_batch_strategy_limited():
    """测试4: 批量运行策略（限制10只股票）"""
    print("\n🧪 测试4: 批量运行策略（限制10只）")
    url = f"{BASE_URL}/api/strategy/run/batch"
    params = {"strategy_code": "ma_bullish", "limit": 10}
    response = requests.post(url, params=params)
    print_response(response, "批量策略运行结果")
    return response.status_code == 200


def test_run_batch_specific_symbols():
    """测试5: 批量运行策略（指定股票列表）"""
    print("\n🧪 测试5: 批量运行策略（指定股票）")
    url = f"{BASE_URL}/api/strategy/run/batch"
    params = {
        "strategy_code": "turtle_trading",
        "symbols": "600519,000001,000002,600000",
    }
    response = requests.post(url, params=params)
    print_response(response, "指定股票批量策略运行结果")
    return response.status_code == 200


def test_query_all_results():
    """测试6: 查询所有策略结果"""
    print("\n🧪 测试6: 查询所有策略结果")
    url = f"{BASE_URL}/api/strategy/results"
    params = {"limit": 20}
    response = requests.get(url, params=params)
    print_response(response, "所有策略结果")
    return response.status_code == 200


def test_query_by_strategy():
    """测试7: 按策略查询结果"""
    print("\n🧪 测试7: 按策略查询结果（海龟交易）")
    url = f"{BASE_URL}/api/strategy/results"
    params = {"strategy_code": "turtle_trading", "limit": 10}
    response = requests.get(url, params=params)
    print_response(response, "海龟交易策略结果")
    return response.status_code == 200


def test_query_by_symbol():
    """测试8: 按股票查询结果"""
    print("\n🧪 测试8: 按股票查询结果（贵州茅台）")
    url = f"{BASE_URL}/api/strategy/results"
    params = {"symbol": "600519", "limit": 10}
    response = requests.get(url, params=params)
    print_response(response, "贵州茅台策略结果")
    return response.status_code == 200


def test_query_matched_only():
    """测试9: 只查询匹配的结果"""
    print("\n🧪 测试9: 只查询匹配的结果")
    url = f"{BASE_URL}/api/strategy/results"
    params = {"match_result": True, "limit": 20}
    response = requests.get(url, params=params)
    print_response(response, "匹配的策略结果")
    return response.status_code == 200


def test_get_matched_stocks():
    """测试10: 获取匹配指定策略的股票列表"""
    print("\n🧪 测试10: 获取匹配策略的股票列表")
    url = f"{BASE_URL}/api/strategy/matched-stocks"
    params = {"strategy_code": "turtle_trading", "limit": 20}
    response = requests.get(url, params=params)
    print_response(response, "匹配海龟交易策略的股票")
    return response.status_code == 200


def test_get_strategy_summary():
    """测试11: 获取策略统计摘要"""
    print("\n🧪 测试11: 获取策略统计摘要")
    url = f"{BASE_URL}/api/strategy/stats/summary"
    response = requests.get(url)
    print_response(response, "策略统计摘要")
    return response.status_code == 200


def test_multiple_strategies():
    """测试12: 测试多个不同的策略"""
    print("\n🧪 测试12: 测试多个不同策略")

    strategies_to_test = [
        "volume_surge",  # 放量上涨
        "ma_bullish",  # 均线多头
        "consolidation_platform",  # 停机坪
        "low_drawdown",  # 无大幅回撤
    ]

    test_symbols = ["600519", "000001", "600000"]

    results = []
    for strategy in strategies_to_test:
        for symbol in test_symbols:
            print(f"\n  运行策略 {strategy} on {symbol}")
            url = f"{BASE_URL}/api/strategy/run/single"
            params = {"strategy_code": strategy, "symbol": symbol}
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "strategy": strategy,
                        "symbol": symbol,
                        "matched": data.get("data", {}).get("match_result", False),
                    }
                )

    print(f"\n{'=' * 60}")
    print("多策略测试结果汇总")
    print(f"{'=' * 60}")
    for r in results:
        status = "✅ 匹配" if r["matched"] else "❌ 不匹配"
        print(f"{status} - {r['strategy']} on {r['symbol']}")

    return len(results) > 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("股票策略系统API测试")
    print("=" * 60)

    tests = [
        ("获取策略定义", test_get_strategy_definitions),
        ("单只股票策略（海龟交易）", test_run_single_strategy),
        ("单只股票策略（放量上涨）", test_run_single_strategy_volume_surge),
        ("批量策略（限制10只）", test_run_batch_strategy_limited),
        ("批量策略（指定股票）", test_run_batch_specific_symbols),
        ("查询所有结果", test_query_all_results),
        ("按策略查询", test_query_by_strategy),
        ("按股票查询", test_query_by_symbol),
        ("只查询匹配结果", test_query_matched_only),
        ("获取匹配股票列表", test_get_matched_stocks),
        ("获取策略统计", test_get_strategy_summary),
        ("多策略综合测试", test_multiple_strategies),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 失败: {e}")
            results.append((name, False))

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 个测试通过")

    # 提示信息
    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print(f"1. 访问 {BASE_URL}/api/docs 查看完整API文档")
    print("2. 策略代码列表:")
    print("   - volume_surge: 放量上涨")
    print("   - ma_bullish: 均线多头")
    print("   - turtle_trading: 海龟交易法则")
    print("   - consolidation_platform: 停机坪")
    print("   - ma250_pullback: 回踩年线")
    print("   - breakthrough_platform: 突破平台")
    print("   - low_drawdown: 无大幅回撤")
    print("   - high_tight_flag: 高而窄的旗形")
    print("   - volume_limit_down: 放量跌停")
    print("   - low_atr_growth: 低ATR成长")
    print("\n3. 批量扫描全市场示例:")
    print("   POST /api/strategy/run/batch?strategy_code=turtle_trading&limit=100")


if __name__ == "__main__":
    main()
