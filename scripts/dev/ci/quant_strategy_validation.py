"""
量化策略验证 - 向后兼容入口

实际实现已拆分至 validators/ 包。
"""

from validators import QuantStrategyValidator  # noqa: F401


def main():
    """CLI 入口"""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="量化策略验证")
    parser.add_argument("strategy_dir", help="策略目录路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    validator = QuantStrategyValidator(args.strategy_dir)
    results = validator.run_full_validation()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    else:
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            passed = sum(1 for r in results.values() if r.get("passed"))
            total = len(results)
            print(f"验证完成: {passed}/{total} 通过")
            for name, result in results.items():
                status = "✅" if result.get("passed") else "❌"
                print(f"  {status} {name}")

    sys.exit(0 if all(r.get("passed") for r in results.values()) else 1)


if __name__ == "__main__":
    main()
