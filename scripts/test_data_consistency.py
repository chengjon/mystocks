#!/usr/bin/env python3
"""端到端数据一致性验证脚本
验证API返回的数据质量和一致性
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import requests


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 配置
BACKEND_PORT = os.getenv("BACKEND_PORT", "").strip()
if not BACKEND_PORT:
    raise RuntimeError("Missing BACKEND_PORT in environment")
API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
HEADERS = {"Content-Type": "application/json"}
if AUTH_TOKEN:
    HEADERS["Authorization"] = f"Bearer {AUTH_TOKEN}"

# 测试统计
TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS = 0


def print_test_result(name: str, passed: bool, message: str = ""):
    """打印测试结果"""
    global TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TOTAL_TESTS += 1

    status = "✓ 通过" if passed else "✗ 失败"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"

    print(f"{color}{status}{reset} {name}")
    if message:
        print(f"    {message}")

    if passed:
        PASSED_TESTS += 1
    else:
        FAILED_TESTS += 1


def test_stocks_basic_api() -> Dict[str, Any]:
    """测试股票基本信息API"""
    print("\n" + "=" * 50)
    print("1. 股票基本信息API验证")
    print("=" * 50)

    try:
        # 测试基本请求
        logger.info("请求股票基本信息...")
        resp = requests.get(
            f"{API_BASE_URL}/api/data/stocks/basic",
            params={"limit": 20},
            headers=HEADERS,
            timeout=10,
        )

        if resp.status_code != 200:
            print_test_result("获取股票基本信息", False, f"HTTP {resp.status_code}")
            return {}

        data = resp.json()

        # 🔴 CRITICAL: 检测HTTP 200 + success=false假阳性问题
        if data.get("success") == False:
            print_test_result(
                "获取股票基本信息",
                False,
                f"假阳性错误: HTTP 200但success=false - {data.get('msg', '未知错误')}",
            )
            return {}

        print_test_result("获取股票基本信息", True)

        # 验证响应结构
        required_fields = ["success", "data", "timestamp"]
        missing = [f for f in required_fields if f not in data]
        print_test_result(
            "响应结构完整性",
            len(missing) == 0,
            f"缺少字段: {missing}" if missing else "所有必需字段都存在",
        )

        # 验证数据格式
        if isinstance(data.get("data"), list):
            print_test_result("数据格式正确", True, f"返回 {len(data['data'])} 条记录")

            # 验证记录完整性
            if data["data"]:
                first_record = data["data"][0]
                required_stock_fields = ["symbol", "name", "industry", "market"]
                missing_fields = [f for f in required_stock_fields if f not in first_record]

                print_test_result(
                    "记录字段完整性",
                    len(missing_fields) == 0,
                    f"缺少字段: {missing_fields}" if missing_fields else "所有股票字段完整",
                )

                # 验证数据质量评分
                quality_score = data.get("data_quality_score", 0)
                print_test_result(
                    "数据质量评分",
                    quality_score >= 70,
                    f"质量评分: {quality_score}/100",
                )

                return data
        else:
            print_test_result("数据格式正确", False, "data 字段应该是数组")
            return {}

    except Exception as e:
        print_test_result("获取股票基本信息", False, str(e))
        return {}


def test_stocks_search_api() -> Dict[str, Any]:
    """测试股票搜索API"""
    print("\n" + "=" * 50)
    print("2. 股票搜索API验证")
    print("=" * 50)

    try:
        logger.info("请求股票搜索...")
        resp = requests.get(
            f"{API_BASE_URL}/api/data/stocks/search",
            params={"keyword": "平安"},
            headers=HEADERS,
            timeout=10,
        )

        if resp.status_code != 200:
            print_test_result("股票搜索", False, f"HTTP {resp.status_code}")
            return {}

        data = resp.json()

        # 🔴 CRITICAL: 检测HTTP 200 + success=false假阳性问题
        if data.get("success") == False:
            print_test_result(
                "股票搜索",
                False,
                f"假阳性错误: HTTP 200但success=false - {data.get('msg', '未知错误')}",
            )
            return {}

        print_test_result("股票搜索", True)

        # 验证搜索结果格式
        if isinstance(data.get("data"), list):
            print_test_result("搜索结果格式", True, f"找到 {len(data['data'])} 条结果")

            if data["data"]:
                # 验证搜索结果与关键词的匹配
                keyword = "平安"
                matched = 0
                for result in data["data"]:
                    if keyword in result.get("name", "") or keyword in result.get(
                        "symbol",
                        "",
                    ):
                        matched += 1

                match_rate = matched / len(data["data"]) if data["data"] else 0
                print_test_result(
                    "搜索结果相关性",
                    match_rate >= 0.8,
                    f"匹配率: {match_rate:.1%}",
                )

                return data
        else:
            print_test_result("搜索结果格式", False, "data 字段应该是数组")
            return {}

    except Exception as e:
        print_test_result("股票搜索", False, str(e))
        return {}


def test_data_consistency(stocks_basic: Dict, stocks_search: Dict) -> None:
    """验证数据一致性"""
    print("\n" + "=" * 50)
    print("3. 数据一致性验证")
    print("=" * 50)

    try:
        if not stocks_basic.get("data") or not stocks_search.get("data"):
            print_test_result("数据一致性检查", False, "缺少基础数据")
            return

        # 提取符号集合
        basic_symbols = {s["symbol"] for s in stocks_basic["data"]}
        search_symbols = {s["symbol"] for s in stocks_search["data"]}

        # 检查搜索结果是否都在基本信息中
        unknown_symbols = search_symbols - basic_symbols
        print_test_result(
            "搜索结果完整性",
            len(unknown_symbols) == 0,
            f"未知符号数: {len(unknown_symbols)}",
        )

        # 检查字段一致性（如果有重叠的符号）
        overlap_symbols = basic_symbols & search_symbols
        if overlap_symbols:
            basic_dict = {s["symbol"]: s for s in stocks_basic["data"]}
            search_dict = {s["symbol"]: s for s in stocks_search["data"]}

            inconsistencies = []
            for symbol in list(overlap_symbols)[:5]:  # 检查前5个
                basic = basic_dict[symbol]
                search = search_dict[symbol]

                for field in ["name", "industry", "market"]:
                    if basic.get(field) != search.get(field):
                        inconsistencies.append(
                            f"{symbol}.{field}: {basic.get(field)} vs {search.get(field)}",
                        )

            print_test_result(
                "字段一致性",
                len(inconsistencies) == 0,
                f"不一致数: {len(inconsistencies)}",
            )

    except Exception as e:
        print_test_result("数据一致性检查", False, str(e))


def test_kline_api() -> Dict[str, Any]:
    """测试K线数据API"""
    print("\n" + "=" * 50)
    print("4. K线数据API验证")
    print("=" * 50)

    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        logger.info(f"请求K线数据 {start_date} 到 {end_date}...")
        resp = requests.get(
            f"{API_BASE_URL}/api/data/stocks/kline",
            params={
                "symbol": "000001.SZ",
                "start_date": start_date,
                "end_date": end_date,
                "period": "day",
            },
            headers=HEADERS,
            timeout=10,
        )

        if resp.status_code != 200:
            print_test_result("获取K线数据", False, f"HTTP {resp.status_code}")
            return {}

        data = resp.json()

        # 🔴 CRITICAL: 检测HTTP 200 + success=false假阳性问题
        if data.get("success") == False:
            print_test_result(
                "获取K线数据",
                False,
                f"假阳性错误: HTTP 200但success=false - {data.get('msg', '未知错误')}",
            )
            return {}

        print_test_result("获取K线数据", True)

        # 验证K线数据结构
        if isinstance(data.get("data"), list):
            print_test_result("K线数据格式", True, f"返回 {len(data['data'])} 条K线")

            if data["data"]:
                first_kline = data["data"][0]
                required_kline_fields = [
                    "date",
                    "open",
                    "close",
                    "high",
                    "low",
                    "volume",
                ]
                missing = [f for f in required_kline_fields if f not in first_kline]

                print_test_result(
                    "K线字段完整性",
                    len(missing) == 0,
                    f"缺少字段: {missing}" if missing else "所有K线字段完整",
                )

                # 验证OHLC关系
                ohlc_valid = True
                for kline in data["data"]:
                    if not (
                        kline["low"] <= kline["open"] <= kline["high"]
                        and kline["low"] <= kline["close"] <= kline["high"]
                    ):
                        ohlc_valid = False
                        break

                print_test_result(
                    "OHLC数据有效性",
                    ohlc_valid,
                    "所有OHLC关系正确" if ohlc_valid else "发现异常OHLC数据",
                )

                return data
        else:
            print_test_result("K线数据格式", False, "data 字段应该是数组")
            return {}

    except Exception as e:
        print_test_result("获取K线数据", False, str(e))
        return {}


def test_monitoring_api() -> None:
    """测试监控API"""
    print("\n" + "=" * 50)
    print("5. 监控API验证")
    print("=" * 50)

    if not AUTH_TOKEN:
        print("⊘ 跳过（未提供AUTH_TOKEN）")
        return

    try:
        logger.info("请求健康检查...")
        resp = requests.get(
            f"{API_BASE_URL}/api/monitoring/health",
            headers=HEADERS,
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            health_status = data.get("data", {}).get("status", "unknown")
            print_test_result("健康检查", True, f"系统状态: {health_status}")
        else:
            print_test_result("健康检查", False, f"HTTP {resp.status_code}")

        logger.info("请求监控仪表板...")
        resp = requests.get(
            f"{API_BASE_URL}/api/monitoring/dashboard",
            headers=HEADERS,
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            dashboard = data.get("data", {})
            success_rate = dashboard.get("success_rate", "N/A")
            print_test_result("监控仪表板", True, f"成功率: {success_rate}")
        else:
            print_test_result("监控仪表板", False, f"HTTP {resp.status_code}")

    except Exception as e:
        print_test_result("监控API", False, str(e))


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("MyStocks API 端到端数据一致性验证")
    print(f"API URL: {API_BASE_URL}")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 运行所有测试
    stocks_basic = test_stocks_basic_api()
    stocks_search = test_stocks_search_api()
    test_data_consistency(stocks_basic, stocks_search)
    test_kline_api()
    test_monitoring_api()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试: {TOTAL_TESTS}")
    print(f"✓ 通过: {PASSED_TESTS}")
    print(f"✗ 失败: {FAILED_TESTS}")
    print("=" * 60)

    if FAILED_TESTS == 0:
        print("✓ 所有测试通过！")
        return 0
    print("✗ 有测试失败，请查看上面的详细信息")
    return 1


if __name__ == "__main__":
    sys.exit(main())
