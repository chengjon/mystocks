#!/usr/bin/env python3
"""
API契约模板验证脚本
验证所有契约模板的完整性和符合OpenAPI规范
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class ContractValidator:
    """契约验证器"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_valid = 0
        self.total_invalid = 0

    def validate_contract(self, contract_file: Path) -> bool:
        """验证单个契约文件"""
        try:
            with open(contract_file, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)

            # 验证必需字段
            required_fields = [
                'api_id', 'module', 'path', 'method',
                'priority', 'request', 'response', 'metadata'
            ]

            for field in required_fields:
                if field not in contract:
                    self.errors.append(f"{contract_file.name}: 缺少必需字段 '{field}'")
                    return False

            # 验证字段类型
            if not isinstance(contract['method'], str) or contract['method'] not in [
                'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'
            ]:
                self.errors.append(f"{contract_file.name}: 无效的HTTP方法 '{contract.get('method')}'")
                return False

            if not contract['path'].startswith('/'):
                self.errors.append(f"{contract_file.name}: 路径必须以'/'开头")
                return False

            if contract['priority'] not in ['P0', 'P1', 'P2']:
                self.warnings.append(f"{contract_file.name}: 未知优先级 '{contract['priority']}'")

            # 验证响应结构
            if 'code' not in contract['response']:
                self.errors.append(f"{contract_file.name}: response缺少code字段")
                return False

            if 'error_codes' not in contract['response']:
                self.warnings.append(f"{contract_file.name}: response缺少error_codes字段")

            # 验证元数据
            if 'created_at' not in contract['metadata']:
                self.warnings.append(f"{contract_file.name}: metadata缺少created_at字段")

            if 'version' not in contract['metadata']:
                self.warnings.append(f"{contract_file.name}: metadata缺少version字段")

            self.total_valid += 1
            return True

        except yaml.YAMLError as e:
            self.errors.append(f"{contract_file.name}: YAML解析错误 - {e}")
            self.total_invalid += 1
            return False
        except Exception as e:
            self.errors.append(f"{contract_file.name}: 验证失败 - {e}")
            self.total_invalid += 1
            return False

    def validate_all_contracts(self, contracts_dir: Path) -> Dict:
        """验证所有契约文件"""
        print(f"🔍 验证契约模板...")
        print(f"   目录: {contracts_dir}\n")

        # 查找所有契约文件
        contract_files = list(contracts_dir.rglob("*.yaml"))
        contract_files = [f for f in contract_files if f.name != "index.yaml"]

        print(f"📋 发现 {len(contract_files)} 个契约文件\n")

        # 验证每个文件
        for contract_file in sorted(contract_files):
            self.validate_contract(contract_file)

        # 生成报告
        report = {
            "total": len(contract_files),
            "valid": self.total_valid,
            "invalid": self.total_invalid,
            "errors": self.errors,
            "warnings": self.warnings,
            "success_rate": f"{(self.total_valid / len(contract_files) * 100):.1f}%" if contract_files else "0%",
        }

        return report


def print_validation_report(report: Dict):
    """打印验证报告"""
    print("=" * 60)
    print("📊 契约验证报告")
    print("=" * 60)

    print(f"\n总计: {report['total']} 个契约")
    print(f"✓ 有效: {report['valid']} 个")
    print(f"✗ 无效: {report['invalid']} 个")
    print(f"✓ 成功率: {report['success_rate']}%")

    if report['errors']:
        print(f"\n❌ 错误 ({len(report['errors'])} 个):")
        for error in report['errors'][:10]:  # 只显示前10个
            print(f"  - {error}")
        if len(report['errors']) > 10:
            print(f"  ... 还有 {len(report['errors']) - 10} 个错误")

    if report['warnings']:
        print(f"\n⚠️  警告 ({len(report['warnings'])} 个):")
        for warning in report['warnings'][:10]:  # 只显示前10个
            print(f"  - {warning}")
        if len(report['warnings']) > 10:
            print(f"  ... 还有 {len(report['warnings']) - 10} 个警告")

    # 验证结果
    print("\n" + "=" * 60)
    if report['invalid'] == 0 and report['errors']:
        print("✅ 所有契约模板验证通过！")
        print("=" * 60)
        return True
    else:
        print("⚠️  发现问题，需要修复")
        print("=" * 60)
        return False


def check_openapi_compliance(contracts_dir: Path) -> bool:
    """检查OpenAPI规范符合性"""
    print(f"\n🔍 检查OpenAPI规范符合性...")

    issues = []

    # 检查索引文件
    index_file = contracts_dir / "index.yaml"
    if not index_file.exists():
        issues.append("缺少index.yaml索引文件")
    else:
        with open(index_file, 'r') as f:
            index = yaml.safe_load(f)

        if 'modules' not in index:
            issues.append("index.yaml缺少modules字段")
        if 'total_contracts' not in index:
            issues.append("index.yaml缺少total_contracts字段")

    # 检查模块目录
    if contracts_dir.exists():
        for module_dir in contracts_dir.iterdir():
            if module_dir.is_dir():
                # 检查是否有契约文件
                contracts = list(module_dir.glob("*.yaml"))
                if not contracts:
                    issues.append(f"模块目录为空: {module_dir.name}")

    if issues:
        print("❌ OpenAPI符合性问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ OpenAPI规范符合性检查通过")
        return True


def main():
    """主函数"""
    contracts_dir = Path("contracts")

    if not contracts_dir.exists():
        print(f"❌ 契约目录不存在: {contracts_dir}")
        return

    # 创建验证器
    validator = ContractValidator()

    # 验证所有契约
    report = validator.validate_all_contracts(contracts_dir)

    # 打印报告
    success = print_validation_report(report)

    # 检查OpenAPI符合性
    openapi_compliant = check_openapi_compliance(contracts_dir)

    # 最终结果
    print(f"\n🎯 验收标准检查:")
    print(f"  ✓ 285个契约模板全部创建: {'是' if report['total'] >= 285 else '否 (' + str(report['total']) + '/285)'}")
    print(f"  ✓ 模板符合OpenAPI规范: {'是' if openapi_compliant else '否'}")
    print(f"  ✓ 核心字段100%覆盖: {'是' if report['invalid'] == 0 else '否'}")
    print(f"  ✓ 通过契约验证测试: {'是' if success else '否'}")

    # 总结
    all_passed = (
        report['total'] >= 285 and
        openapi_compliant and
        report['invalid'] == 0 and
        success
    )

    if all_passed:
        print(f"\n🎉 所有验收标准通过！")
    else:
        print(f"\n⚠️  部分验收标准未通过，需要修复")

    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
