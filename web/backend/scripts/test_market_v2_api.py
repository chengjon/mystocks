#!/usr/bin/env python3
"""
测试市场数据V2 API端点
测试东方财富直接API的各项功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


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


def test_etf_refresh():
    """测试ETF数据刷新"""
    print("\n🧪 测试1: 刷新ETF数据")
    url = f"{BASE_URL}/api/market/v2/etf/refresh"
    response = requests.post(url)
    print_response(response, "ETF数据刷新")
    return response.status_code == 200


def test_etf_query():
    """测试ETF数据查询"""
    print("\n🧪 测试2: 查询ETF数据（前10个）")
    url = f"{BASE_URL}/api/market/v2/etf/list?limit=10"
    response = requests.get(url)
    print_response(response, "ETF数据查询")
    return response.status_code == 200


def test_fund_flow_refresh():
    """测试资金流向刷新（茅台）"""
    print("\n🧪 测试3: 刷新贵州茅台资金流向")
    url = f"{BASE_URL}/api/market/v2/fund-flow/refresh?symbol=600519&timeframe=今日"
    response = requests.post(url)
    print_response(response, "资金流向刷新")
    return response.status_code == 200


def test_fund_flow_query():
    """测试资金流向查询"""
    print("\n🧪 测试4: 查询贵州茅台资金流向")
    url = f"{BASE_URL}/api/market/v2/fund-flow?symbol=600519&timeframe=1"
    response = requests.get(url)
    print_response(response, "资金流向查询")
    return response.status_code == 200


def test_sector_fund_flow_refresh():
    """测试行业资金流向刷新"""
    print("\n🧪 测试5: 刷新行业资金流向")
    url = f"{BASE_URL}/api/market/v2/sector/fund-flow/refresh?sector_type=行业&timeframe=今日"
    response = requests.post(url)
    print_response(response, "行业资金流向刷新")
    return response.status_code == 200


def test_sector_fund_flow_query():
    """测试行业资金流向查询"""
    print("\n🧪 测试6: 查询行业资金流向（前10个）")
    url = f"{BASE_URL}/api/market/v2/sector/fund-flow?sector_type=行业&timeframe=今日&limit=10"
    response = requests.get(url)
    print_response(response, "行业资金流向查询")
    return response.status_code == 200


def test_lhb_refresh():
    """测试龙虎榜刷新"""
    print("\n🧪 测试7: 刷新龙虎榜数据（最近交易日）")
    # 使用最近的交易日日期
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/api/market/v2/lhb/refresh?trade_date={today}"
    response = requests.post(url)
    print_response(response, "龙虎榜刷新")
    return response.status_code == 200


def test_lhb_query():
    """测试龙虎榜查询"""
    print("\n🧪 测试8: 查询龙虎榜数据（最近20条）")
    url = f"{BASE_URL}/api/market/v2/lhb?limit=20"
    response = requests.get(url)
    print_response(response, "龙虎榜查询")
    return response.status_code == 200


def test_dividend_refresh():
    """测试分红配送刷新"""
    print("\n🧪 测试9: 刷新贵州茅台分红配送数据")
    url = f"{BASE_URL}/api/market/v2/dividend/refresh?symbol=600519"
    response = requests.post(url)
    print_response(response, "分红配送刷新")
    return response.status_code == 200


def test_dividend_query():
    """测试分红配送查询"""
    print("\n🧪 测试10: 查询贵州茅台分红配送数据")
    url = f"{BASE_URL}/api/market/v2/dividend?symbol=600519&limit=10"
    response = requests.get(url)
    print_response(response, "分红配送查询")
    return response.status_code == 200


def test_blocktrade_refresh():
    """测试大宗交易刷新"""
    print("\n🧪 测试11: 刷新大宗交易数据")
    url = f"{BASE_URL}/api/market/v2/blocktrade/refresh"
    response = requests.post(url)
    print_response(response, "大宗交易刷新")
    return response.status_code == 200


def test_blocktrade_query():
    """测试大宗交易查询"""
    print("\n🧪 测试12: 查询大宗交易数据（最近20条）")
    url = f"{BASE_URL}/api/market/v2/blocktrade?limit=20"
    response = requests.get(url)
    print_response(response, "大宗交易查询")
    return response.status_code == 200


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("市场数据V2 API测试")
    print("=" * 60)

    tests = [
        ("ETF数据刷新", test_etf_refresh),
        ("ETF数据查询", test_etf_query),
        ("资金流向刷新", test_fund_flow_refresh),
        ("资金流向查询", test_fund_flow_query),
        ("行业资金流向刷新", test_sector_fund_flow_refresh),
        ("行业资金流向查询", test_sector_fund_flow_query),
        ("龙虎榜刷新", test_lhb_refresh),
        ("龙虎榜查询", test_lhb_query),
        ("分红配送刷新", test_dividend_refresh),
        ("分红配送查询", test_dividend_query),
        ("大宗交易刷新", test_blocktrade_refresh),
        ("大宗交易查询", test_blocktrade_query),
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


if __name__ == "__main__":
    main()
