#!/usr/bin/env python3
"""Run data sync API contract tests (demo script)."""

from tests.api_contract_tests import run_data_sync_tests


def main() -> None:
    try:
        results = run_data_sync_tests()
        print("✅ API契约测试完成")
        print(f"   测试通过率: {results['api_contracts']['summary']['success_rate']}%")
    except Exception as exc:
        print(f"❌ API契约测试失败: {exc}")
        print("   注意: 这是一个演示，实际运行需要后端服务")


if __name__ == "__main__":
    main()
