#!/usr/bin/env python3
"""
P0 API功能测试脚本

测试核心P0级别API端点的功能正确性和性能

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not installed, using requests instead")
    import requests

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试结果存储
test_results = []

# P0核心API端点列表（根据OpenAPI配置）
P0_APIS = [
    # Health API
    {
        "name": "Health Check",
        "method": "GET",
        "path": "/health",
        "module": "health",
        "description": "系统健康检查",
        "priority": "P0",
    },
    # Market API
    {
        "name": "Market Overview",
        "method": "GET",
        "path": "/api/data/markets/overview",
        "module": "market",
        "description": "市场概览数据",
        "priority": "P0",
    },
    {
        "name": "Real-time Quotes",
        "method": "GET",
        "path": "/api/market/quotes",
        "module": "market",
        "description": "实时行情数据",
        "priority": "P0",
    },
    # Cache API
    {
        "name": "Cache Statistics",
        "method": "GET",
        "path": "/api/cache/status",
        "module": "cache",
        "description": "缓存统计信息",
        "priority": "P0",
    },
    {
        "name": "Cache Health Check",
        "method": "GET",
        "path": "/api/cache/monitoring/health",
        "module": "cache",
        "description": "缓存健康检查",
        "priority": "P0",
    },
    # System API
    {
        "name": "System Health Check",
        "method": "GET",
        "path": "/api/system/health",
        "module": "system",
        "description": "系统健康检查",
        "priority": "P0",
    },
    # Data API
    {
        "name": "Stock Basic Info",
        "method": "GET",
        "path": "/api/data/stocks/basic",
        "module": "data",
        "description": "股票基本信息",
        "priority": "P0",
    },
]


class Colors:
    """ANSI颜色代码"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_success(msg: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")


def print_error(msg: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗{Colors.NC} {msg}")


def print_info(msg: str):
    """打印信息消息"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")


def print_warning(msg: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")


async def test_api_async(client: httpx.AsyncClient, api: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试单个API端点（异步）

    Args:
        client: HTTP客户端
        api: API配置

    Returns:
        测试结果字典
    """
    url = f"{BASE_URL}{api['path']}"
    method = api['method'].lower()

    result = {
        "name": api['name'],
        "method": api['method'],
        "path": api['path'],
        "module": api['module'],
        "priority": api['priority'],
        "success": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "response_size": 0,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # 记录开始时间
        start_time = time.time()

        # 发送请求
        if method == "get":
            response = await client.get(url, timeout=10.0)
        elif method == "post":
            response = await client.post(url, timeout=10.0)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # 计算响应时间
        response_time = (time.time() - start_time) * 1000
        result['response_time_ms'] = round(response_time, 2)
        result['status_code'] = response.status_code
        result['response_size'] = len(response.content)

        # 检查状态码
        if response.status_code in [200, 201]:
            result['success'] = True

            # 尝试解析JSON
            try:
                data = response.json()
                result['has_json'] = True
                result['json_keys'] = list(data.keys()) if isinstance(data, dict) else None
            except:
                result['has_json'] = False
        else:
            result['error'] = f"HTTP {response.status_code}"

    except asyncio.TimeoutError:
        result['error'] = "Timeout"
        result['response_time_ms'] = 10000  # 10秒超时

    except httpx.ConnectError:
        result['error'] = "Connection refused"

    except Exception as e:
        result['error'] = str(e)

    return result


def test_api_sync(api: Dict[str, Any]) -> Dict[str, Any]:
    """
    测试单个API端点（同步，使用requests）

    Args:
        api: API配置

    Returns:
        测试结果字典
    """
    url = f"{BASE_URL}{api['path']}"
    method = api['method'].lower()

    result = {
        "name": api['name'],
        "method": api['method'],
        "path": api['path'],
        "module": api['module'],
        "priority": api['priority'],
        "success": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "response_size": 0,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # 记录开始时间
        start_time = time.time()

        # 发送请求
        if method == "get":
            response = requests.get(url, timeout=10)
        elif method == "post":
            response = requests.post(url, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # 计算响应时间
        response_time = (time.time() - start_time) * 1000
        result['response_time_ms'] = round(response_time, 2)
        result['status_code'] = response.status_code
        result['response_size'] = len(response.content)

        # 检查状态码
        if response.status_code in [200, 201]:
            result['success'] = True

            # 尝试解析JSON
            try:
                data = response.json()
                result['has_json'] = True
                result['json_keys'] = list(data.keys()) if isinstance(data, dict) else None
            except:
                result['has_json'] = False
        else:
            result['error'] = f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        result['error'] = "Timeout"
        result['response_time_ms'] = 10000  # 10秒超时

    except requests.exceptions.ConnectionError:
        result['error'] = "Connection refused"

    except Exception as e:
        result['error'] = str(e)

    return result


async def test_all_apis_async() -> List[Dict[str, Any]]:
    """
    异步测试所有API端点
    """
    print_info(f"开始测试 {len(P0_APIS)} 个P0 API端点...")
    print_info(f"目标服务器: {BASE_URL}")
    print()

    results = []

    async with httpx.AsyncClient() as client:
        for api in P0_APIS:
            print_info(f"测试: {api['name']} ({api['method']} {api['path']})")
            result = await test_api_async(client, api)
            results.append(result)

            if result['success']:
                print_success(f"{api['name']} - {result['response_time_ms']}ms")
            else:
                print_error(f"{api['name']} - {result['error']}")

    return results


def test_all_apis_sync() -> List[Dict[str, Any]]:
    """
    同步测试所有API端点
    """
    print_info(f"开始测试 {len(P0_APIS)} 个P0 API端点...")
    print_info(f"目标服务器: {BASE_URL}")
    print()

    results = []

    for api in P0_APIS:
        print_info(f"测试: {api['name']} ({api['method']} {api['path']})")
        result = test_api_sync(api)
        results.append(result)

        if result['success']:
            print_success(f"{api['name']} - {result['response_time_ms']}ms")
        else:
            print_error(f"{api['name']} - {result['error']}")

    return results


def generate_test_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成测试报告

    Args:
        results: 测试结果列表

    Returns:
        报告字典
    """
    total = len(results)
    success = sum(1 for r in results if r['success'])
    failed = total - success

    # 计算平均响应时间（仅成功的请求）
    successful_results = [r for r in results if r['success']]
    avg_response_time = (
        sum(r['response_time_ms'] for r in successful_results) / len(successful_results)
        if successful_results else 0
    )

    # 按模块分组
    modules = {}
    for result in results:
        module = result['module']
        if module not in modules:
            modules[module] = {"total": 0, "success": 0, "failed": 0, "response_times": []}

        modules[module]["total"] += 1
        if result['success']:
            modules[module]["success"] += 1
            modules[module]["response_times"].append(result['response_time_ms'])
        else:
            modules[module]["failed"] += 1

    # 计算每个模块的平均响应时间
    for module in modules:
        if modules[module]["response_times"]:
            modules[module]["avg_response_time"] = round(
                sum(modules[module]["response_times"]) / len(modules[module]["response_times"]), 2
            )
        else:
            modules[module]["avg_response_time"] = None

    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
        },
        "by_module": modules,
        "details": results,
    }


def print_test_report(report: Dict[str, Any]):
    """打印测试报告"""
    print()
    print("=" * 70)
    print("P0 API 测试报告")
    print("=" * 70)
    print()

    # 打印汇总
    summary = report['summary']
    print(f"测试时间: {report['timestamp']}")
    print(f"总计: {summary['total']} 个端点")
    print(f"成功: {summary['success']} 个")
    print(f"失败: {summary['failed']} 个")
    print(f"成功率: {summary['success_rate']}%")
    print(f"平均响应时间: {summary['avg_response_time_ms']} ms")
    print()

    # 按模块统计
    print("按模块统计:")
    print()
    for module, stats in report['by_module'].items():
        print(f"  {module}:")
        print(f"    - 总计: {stats['total']}")
        print(f"    - 成功: {stats['success']}")
        print(f"    - 失败: {stats['failed']}")
        print(f"    - 平均响应时间: {stats.get('avg_response_time', 'N/A')} ms")
    print()

    # 失败的API详情
    failed_apis = [r for r in report['details'] if not r['success']]
    if failed_apis:
        print("失败的API:")
        print()
        for api in failed_apis:
            print(f"  - {api['name']} ({api['path']})")
            print(f"    错误: {api['error']}")
        print()

    # 成功的API响应时间排行
    successful_apis = [r for r in report['details'] if r['success']]
    if successful_apis:
        print("响应时间排行 (从快到慢):")
        print()
        sorted_apis = sorted(successful_apis, key=lambda x: x['response_time_ms'])
        for i, api in enumerate(sorted_apis[:10], 1):
            print(f"  {i}. {api['name']}: {api['response_time_ms']} ms")
        print()

    print("=" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("P0 API 功能测试")
    print("=" * 70)
    print()

    # 检查服务器是否运行
    print_info("检查服务器连接...")
    try:
        if HTTPX_AVAILABLE:
            response = asyncio.run(httpx.AsyncClient().get(f"{BASE_URL}/health", timeout=5.0))
        else:
            response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            print_success("服务器连接正常")
        else:
            print_warning(f"服务器返回状态码: {response.status_code}")
    except Exception as e:
        print_error(f"无法连接到服务器: {e}")
        print_error(f"请确保FastAPI服务正在运行: python run_server.py")
        print()
        return

    print()

    # 运行测试
    try:
        if HTTPX_AVAILABLE:
            results = asyncio.run(test_all_apis_async())
        else:
            results = test_all_apis_sync()

        # 生成报告
        report = generate_test_report(results)

        # 打印报告
        print_test_report(report)

        # 保存报告到文件
        report_file = "/opt/claude/mystocks_phase7_backend/reports/p0_api_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print_info(f"测试报告已保存到: {report_file}")

    except Exception as e:
        print_error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
