#!/usr/bin/env python3
"""MyStocks Web Mock数据覆盖率快速检查

检查API文件是否支持Mock数据
"""

from pathlib import Path


def check_api_mock_support():
    """检查每个API文件是否支持Mock数据"""
    api_dir = Path(__file__).parent.parent / "api"

    print("🔍 MyStocks Mock数据支持检查")
    print("=" * 60)
    print("📅 检查时间: 2025-11-13 21:03:30")
    print()

    supported_apis = []
    unsupported_apis = []

    for py_file in sorted(api_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
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

            print(f"{status} {py_file.stem:25} {'Mock数据支持' if has_mock_support else '缺少Mock支持'}")

        except Exception as e:
            print(f"⚠️  {py_file.stem:25} 读取错误: {e}")

    print()
    print("📊 覆盖率统计:")
    print("-" * 30)
    total_apis = len(supported_apis) + len(unsupported_apis)
    coverage_rate = len(supported_apis) / total_apis * 100 if total_apis > 0 else 0

    print(f"总API文件数: {total_apis}")
    print(f"支持Mock数据: {len(supported_apis)}")
    print(f"缺少Mock数据: {len(unsupported_apis)}")
    print(f"覆盖率: {coverage_rate:.1f}%")

    if unsupported_apis:
        print()
        print("❌ 需要添加Mock数据支持的API:")
        print("-" * 40)
        for api in unsupported_apis:
            print(f"  • {api}.py")

    return {
        "total": total_apis,
        "supported": len(supported_apis),
        "unsupported": len(unsupported_apis),
        "coverage_rate": coverage_rate,
        "missing_apis": unsupported_apis,
    }


if __name__ == "__main__":
    result = check_api_mock_support()
