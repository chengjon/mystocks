#!/usr/bin/env python3
"""验证P1 API契约文件

验证所有P1契约的完整性和正确性。

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import yaml
from pathlib import Path


def validate_contracts():
    """验证P1契约文件"""
    p1_dir = Path("/opt/claude/mystocks_phase7_backend/contracts/p1")

    if not p1_dir.exists():
        print(f"❌ P1契约目录不存在: {p1_dir}")
        return False

    issues = []
    total = 0

    print(f"🔍 开始验证P1 API契约")
    print(f"   目录: {p1_dir}")
    print()

    # 遍历所有YAML文件
    for yaml_file in sorted(p1_dir.rglob("*.yaml")):
        if yaml_file.name == "index.yaml":
            continue

        total += 1

        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                contract = yaml.safe_load(f)

            # 验证必需字段
            required_fields = [
                "api_id", "priority", "module", "path",
                "method", "description", "request_params", "response"
            ]

            for field in required_fields:
                if field not in contract:
                    issues.append(f"{yaml_file.name}: 缺少字段 {field}")

            # 验证priority
            if contract.get("priority") != "P1":
                issues.append(f"{yaml_file.name}: priority应为P1，实际为{contract.get('priority')}")

            # 验证method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "WS"]
            if contract.get("method") not in valid_methods:
                issues.append(f"{yaml_file.name}: 无效的method {contract.get('method')}")

            # 验证module
            valid_modules = ["backtest", "risk", "user", "trade", "technical", "dashboard", "data", "sse", "tasks", "market"]
            if contract.get("module") not in valid_modules:
                issues.append(f"{yaml_file.name}: 无效的module {contract.get('module')}")

            # 验证response结构
            response = contract.get("response", {})
            if "success_code" not in response:
                issues.append(f"{yaml_file.name}: response缺少success_code")

            if "error_codes" not in response:
                issues.append(f"{yaml_file.name}: response缺少error_codes")

            # 打印进度
            if total % 10 == 0:
                print(f"   已验证: {total}个...")

        except yaml.YAMLError as e:
            issues.append(f"{yaml_file.name}: YAML解析错误 - {str(e)}")
        except Exception as e:
            issues.append(f"{yaml_file.name}: 读取错误 - {str(e)}")

    print()
    print("=" * 60)
    print(f"📊 验证统计:")
    print(f"   总计: {total}个契约")
    print(f"   问题: {len(issues)}个")
    print()

    # 报告问题
    if issues:
        print("❌ 发现问题:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        return False
    else:
        print("✅ 所有契约验证通过!")
        print()

        # 按模块统计
        print("📊 模块分布:")
        for module_dir in sorted(p1_dir.iterdir()):
            if module_dir.is_dir() and module_dir.name != "__pycache__":
                count = len(list(module_dir.glob("*.yaml")))
                print(f"   - {module_dir.name}: {count}个契约")
        print()

        return True


if __name__ == "__main__":
    success = validate_contracts()
    exit(0 if success else 1)
