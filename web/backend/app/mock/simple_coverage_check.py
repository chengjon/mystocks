#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks Web Mock数据覆盖率快速检查

检查API文件是否支持Mock数据
"""

from pathlib import Path

from app.core.logger import logger


def check_api_mock_support():
    """检查每个API文件是否支持Mock数据"""
    api_dir = Path(__file__).parent.parent / "api"

    logger.info("🔍 MyStocks Mock数据支持检查")
    logger.info("=" * 60)
    logger.info("📅 检查时间: 2025-11-13 21:03:30")
    logger.info("")

    supported_apis = []
    unsupported_apis = []

    for py_file in sorted(api_dir.glob("*.py")):
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

            if has_mock_support:
                supported_apis.append(py_file.stem)
                status = "✅"
            else:
                unsupported_apis.append(py_file.stem)
                status = "❌"

            logger.info(f"{status} {py_file.stem:25} {'Mock数据支持' if has_mock_support else '缺少Mock支持'}")

        except Exception as e:
            logger.error("读取错误 %s: %s", py_file.stem, e)

    logger.info("")
    logger.info("📊 覆盖率统计:")
    logger.info("-" * 30)
    total_apis = len(supported_apis) + len(unsupported_apis)
    coverage_rate = len(supported_apis) / total_apis * 100 if total_apis > 0 else 0

    logger.info(f"总API文件数: {total_apis}")
    logger.info(f"支持Mock数据: {len(supported_apis)}")
    logger.info(f"缺少Mock数据: {len(unsupported_apis)}")
    logger.info(f"覆盖率: {coverage_rate:.1f}%")

    if unsupported_apis:
        logger.info("")
        logger.info("❌ 需要添加Mock数据支持的API:")
        logger.info("-" * 40)
        for api in unsupported_apis:
            logger.info(f"  • {api}.py")

    return {
        "total": total_apis,
        "supported": len(supported_apis),
        "unsupported": len(unsupported_apis),
        "coverage_rate": coverage_rate,
        "missing_apis": unsupported_apis,
    }


if __name__ == "__main__":
    result = check_api_mock_support()
