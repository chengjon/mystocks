#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks Web Mock数据覆盖率分析报告

分析前端API调用与Mock数据支持的匹配度，识别缺失的Mock数据支持

作者: Claude Code
创建时间: 2025-11-13
"""

import re
from pathlib import Path
from typing import Dict, List, Set

from app.core.logger import logger


def scan_api_files() -> Dict[str, List[str]]:
    """扫描所有API文件，提取API端点"""
    api_dir = Path(__file__).parent.parent / "api"
    api_endpoints = {}

    for py_file in api_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        endpoints = []
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取@router.get装饰的端点
            get_pattern = r'@router\.get\(["\']([^"\']*)["\']'
            get_matches = re.findall(get_pattern, content)
            endpoints.extend(get_matches)

            # 提取@router.post装饰的端点
            post_pattern = r'@router\.post\(["\']([^"\']*)["\']'
            post_matches = re.findall(post_pattern, content)
            endpoints.extend(post_matches)

            # 提取@router.put装饰的端点
            put_pattern = r'@router\.put\(["\']([^"\']*)["\']'
            put_matches = re.findall(put_pattern, content)
            endpoints.extend(put_matches)

            # 提取@router.delete装饰的端点
            delete_pattern = r'@router\.delete\(["\']([^"\']*)["\']'
            delete_matches = re.findall(delete_pattern, content)
            endpoints.extend(delete_matches)

        except Exception as e:
            logger.error("Error reading %s: %s", py_file, e)

        api_endpoints[py_file.stem] = endpoints

    return api_endpoints


def scan_frontend_api_calls() -> Set[str]:
    """扫描前端Vue文件中的API调用"""
    frontend_dir = Path(__file__).parent.parent.parent.parent / "web" / "frontend" / "src"
    api_calls = set()

    for vue_file in frontend_dir.rglob("*.vue"):
        try:
            with open(vue_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取API调用路径
            api_patterns = [
                r'["\']\/api\/([^"\']*)["\']',
                r'axios\.get\(["\']([^"\']*)["\']',
                r'axios\.post\(["\']([^"\']*)["\']',
                r'axios\.put\(["\']([^"\']*)["\']',
                r'axios\.delete\(["\']([^"\']*)["\']',
                r'fetch\(["\']([^"\']*)["\']',
            ]

            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.startswith("api/"):
                        api_calls.add(match)
                    elif match.startswith("/"):
                        api_calls.add(match.strip("/"))

        except Exception as e:
            logger.error("Error reading %s: %s", vue_file, e)

    return api_calls


def check_mock_support() -> Dict[str, bool]:
    """检查每个API文件是否支持Mock数据"""
    api_dir = Path(__file__).parent.parent / "api"
    mock_support = {}

    for py_file in api_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否包含Mock数据相关代码
            mock_indicators = [
                "USE_MOCK_DATA",
                "get_mock_data_manager",
                "mock_data",
                "mock_manager",
            ]

            has_mock_support = any(indicator in content for indicator in mock_indicators)
            mock_support[py_file.stem] = has_mock_support

        except Exception as e:
            logger.error("Error reading %s: %s", py_file, e)
            mock_support[py_file.stem] = False

    return mock_support


def generate_coverage_report():
    """生成Mock数据覆盖率报告"""
    logger.info("🔍 MyStocks Mock数据覆盖率分析")
    logger.info("=" * 80)
    logger.info("📅 分析时间: 2025-11-13 21:03:00")
    logger.info("")

    # 扫描API端点
    api_endpoints = scan_api_files()
    logger.info(f"📊 发现API文件: {len(api_endpoints)}个")

    # 检查Mock支持
    mock_support = check_mock_support()

    # 扫描前端API调用
    frontend_calls = scan_frontend_api_calls()
    logger.info(f"📱 发现前端API调用: {len(frontend_calls)}个")
    logger.info("")

    # 分析覆盖率
    logger.info("🎯 API文件Mock数据支持状态:")
    logger.info("-" * 80)

    supported_count = 0
    total_count = len(mock_support)

    for api_name in sorted(mock_support.keys()):
        is_supported = mock_support[api_name]
        status = "✅ 支持" if is_supported else "❌ 不支持"

        # 统计该API的端点数量
        endpoint_count = len(api_endpoints.get(api_name, []))

        logger.info(f"{api_name:20} {status:10} ({endpoint_count:2}个端点)")

        if is_supported:
            supported_count += 1

    logger.info("")
    logger.info(f"📈 Mock数据覆盖率: {supported_count}/{total_count} ({supported_count / total_count * 100:.1f}%)")
    logger.info("")

    # 列出缺失Mock数据的API
    missing_apis = [api for api, supported in mock_support.items() if not supported]

    if missing_apis:
        logger.info("❌ 缺少Mock数据支持的API文件:")
        logger.info("-" * 50)
        for api in missing_apis:
            endpoints = api_endpoints.get(api, [])
            logger.info(f"  • {api}.py ({len(endpoints)}个端点)")
            for endpoint in endpoints[:3]:  # 只显示前3个端点
                logger.info(f"    - {endpoint}")
            if len(endpoints) > 3:
                logger.info(f"    - ... 还有{len(endpoints) - 3}个端点")
        logger.info("")

    # 分析前端API调用与Mock支持匹配度
    logger.info("🔍 前端API调用与Mock数据匹配分析:")
    logger.info("-" * 50)

    # 根据API文件分组前端调用
    api_usage = {}
    for call in frontend_calls:
        # 提取API路径前缀
        if call.startswith("api/market/"):
            api_usage.setdefault("market", []).append(call)
        elif call.startswith("api/system/"):
            api_usage.setdefault("system", []).append(call)
        elif call.startswith("api/tasks/"):
            api_usage.setdefault("tasks", []).append(call)
        elif call.startswith("api/technical"):
            api_usage.setdefault("technical_analysis", []).append(call)
        elif call.startswith("api/strategy"):
            api_usage.setdefault("strategy_management", []).append(call)
        elif call.startswith("api/monitoring"):
            api_usage.setdefault("monitoring", []).append(call)
        elif call.startswith("api/wencai"):
            api_usage.setdefault("wencai", []).append(call)
        elif call.startswith("api/tdx"):
            api_usage.setdefault("tdx", []).append(call)
        elif call.startswith("api/data"):
            api_usage.setdefault("data", []).append(call)
        elif call.startswith("api/auth"):
            api_usage.setdefault("auth", []).append(call)
        elif call.startswith("api/watchlist"):
            api_usage.setdefault("watchlist", []).append(call)
        else:
            api_usage.setdefault("other", []).append(call)

    logger.info("前端API调用分布:")
    for api_name, calls in api_usage.items():
        mock_status = "✅" if mock_support.get(api_name, False) else "❌"
        logger.info(f"  {api_name:20} {mock_status} ({len(calls)}个调用)")

    logger.info("")

    # 提供建议
    logger.info("💡 改进建议:")
    logger.info("-" * 30)

    priority_apis = []
    for api in missing_apis:
        # 基于前端调用频次确定优先级
        call_count = len(api_usage.get(api, []))
        if call_count > 0:
            priority_apis.append((api, call_count))

    # 按调用频次排序
    priority_apis.sort(key=lambda x: x[1], reverse=True)

    if priority_apis:
        logger.info("建议优先添加Mock数据支持的API (按前端调用频次排序):")
        for api, count in priority_apis[:5]:
            logger.info(f"  • {api}.py (前端调用{count}次)")
    else:
        logger.info("✅ 所有前端调用的API都有Mock数据支持")

    logger.info("")
    logger.info("=" * 80)
    logger.info("🎯 覆盖率目标: 100% Mock数据支持")
    logger.info(f"📊 当前进度: {supported_count}/{total_count} ({supported_count / total_count * 100:.1f}%)")

    return {
        "total_apis": total_count,
        "supported_apis": supported_count,
        "missing_apis": missing_apis,
        "coverage_rate": supported_count / total_count * 100,
        "frontend_calls": len(frontend_calls),
        "api_endpoints": api_endpoints,
    }


if __name__ == "__main__":
    result = generate_coverage_report()
