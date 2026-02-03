#!/usr/bin/env python3
"""
OpenAPI契约差异检测脚本
用于CI/CD流水线中自动检测API契约的破坏性变更
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml
    from deepdiff import DeepDiff
except ImportError:
    print("❌ 缺少依赖: pip install pyyaml deepdiff")
    sys.exit(1)


class ContractDiffer:
    """契约差异检测器"""

    # 破坏性变更模式
    BREAKING_PATTERNS = {
        "paths_removed": "删除API端点",
        "path_method_removed": "删除HTTP方法",
        "request_param_removed": "删除请求参数",
        "response_field_removed": "删除响应字段",
        "required_param_added": "新增必填请求参数",
        "type_changed": "修改字段类型",
    }

    def __init__(self, base_path: str, head_path: str):
        self.base_path = Path(base_path)
        self.head_path = Path(head_path)
        self.breaking_changes: List[Dict] = []
        self.non_breaking_changes: List[Dict] = []

    def load_contract(self, path: Path) -> Dict[str, Any]:
        """加载OpenAPI契约文件"""
        if not path.exists():
            raise FileNotFoundError(f"契约文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif path.suffix == ".json":
                return json.load(f)
            else:
                raise ValueError(f"不支持的文件格式: {path.suffix}")

    def compare_paths(self, base_spec: Dict, head_spec: Dict):
        """对比API路径变更"""
        base_paths = base_spec.get("paths", {})
        head_paths = head_spec.get("paths", {})

        # 检测删除的端点
        for path in base_paths:
            if path not in head_paths:
                self.breaking_changes.append({
                    "type": "paths_removed",
                    "path": f"paths.{path}",
                    "message": f"删除API端点: {path}",
                    "severity": "critical"
                })

        # 检测新增的端点 (非破坏性)
        for path in head_paths:
            if path not in base_paths:
                self.non_breaking_changes.append({
                    "type": "path_added",
                    "path": f"paths.{path}",
                    "message": f"新增API端点: {path}",
                    "severity": "info"
                })

        # 检测路径内的方法变更
        for path in base_paths:
            if path in head_paths:
                self.compare_path_methods(path, base_paths[path], head_paths[path])

    def compare_path_methods(self, path: str, base_path_spec: Dict, head_path_spec: Dict):
        """对比HTTP方法变更"""
        base_methods = set(base_path_spec.keys()) & {"get", "post", "put", "delete", "patch"}
        head_methods = set(head_path_spec.keys()) & {"get", "post", "put", "delete", "patch"}

        # 检测删除的方法
        for method in base_methods:
            if method not in head_methods:
                self.breaking_changes.append({
                    "type": "path_method_removed",
                    "path": f"paths.{path}.{method}",
                    "message": f"删除HTTP方法: {method.upper()} {path}",
                    "severity": "critical"
                })

        # 检测新增的方法 (非破坏性)
        for method in head_methods:
            if method not in base_methods:
                self.non_breaking_changes.append({
                    "type": "method_added",
                    "path": f"paths.{path}.{method}",
                    "message": f"新增HTTP方法: {method.upper()} {path}",
                    "severity": "info"
                })

    def compare_schemas(self, base_spec: Dict, head_spec: Dict):
        """对比Schema定义变更"""
        base_schemas = base_spec.get("components", {}).get("schemas", {})
        head_schemas = head_spec.get("components", {}).get("schemas", {})

        # 检测删除的Schema
        for schema_name in base_schemas:
            if schema_name not in head_schemas:
                self.breaking_changes.append({
                    "type": "schema_removed",
                    "path": f"components.schemas.{schema_name}",
                    "message": f"删除Schema定义: {schema_name}",
                    "severity": "high"
                })

        # 检测新增的Schema (非破坏性)
        for schema_name in head_schemas:
            if schema_name not in base_schemas:
                self.non_breaking_changes.append({
                    "type": "schema_added",
                    "path": f"components.schemas.{schema_name}",
                    "message": f"新增Schema定义: {schema_name}",
                    "severity": "info"
                })

        # 对比Schema字段变更
        for schema_name in base_schemas:
            if schema_name in head_schemas:
                self.compare_schema_fields(
                    schema_name,
                    base_schemas[schema_name],
                    head_schemas[schema_name]
                )

    def compare_schema_fields(self, schema_name: str, base_schema: Dict, head_schema: Dict):
        """对比Schema字段变更"""
        base_props = base_schema.get("properties", {})
        head_props = head_schema.get("properties", {})
        base_required = set(base_schema.get("required", []))
        head_required = set(head_schema.get("required", []))

        # 检测删除的字段
        for field_name in base_props:
            if field_name not in head_props:
                # 如果是必填字段，则是破坏性变更
                if field_name in base_required:
                    self.breaking_changes.append({
                        "type": "required_field_removed",
                        "path": f"components.schemas.{schema_name}.properties.{field_name}",
                        "message": f"删除必填字段: {schema_name}.{field_name}",
                        "severity": "high"
                    })
                else:
                    self.non_breaking_changes.append({
                        "type": "optional_field_removed",
                        "path": f"components.schemas.{schema_name}.properties.{field_name}",
                        "message": f"删除可选字段: {schema_name}.{field_name}",
                        "severity": "low"
                    })

        # 检测新增的必填字段 (破坏性变更)
        for field_name in head_props:
            if field_name not in base_props and field_name in head_required:
                self.breaking_changes.append({
                    "type": "required_param_added",
                    "path": f"components.schemas.{schema_name}.properties.{field_name}",
                    "message": f"新增必填字段: {schema_name}.{field_name}",
                    "severity": "high"
                })

        # 检测新增的可选字段 (非破坏性)
        for field_name in head_props:
            if field_name not in base_props and field_name not in head_required:
                self.non_breaking_changes.append({
                    "type": "optional_param_added",
                    "path": f"components.schemas.{schema_name}.properties.{field_name}",
                    "message": f"新增可选字段: {schema_name}.{field_name}",
                    "severity": "info"
                })

        # 检测字段类型变更
        for field_name in base_props:
            if field_name in head_props:
                base_type = base_props[field_name].get("type")
                head_type = head_props[field_name].get("type")

                if base_type != head_type:
                    # 检查是否兼容 (如: string -> format: string)
                    if not self.is_type_compatible(base_type, head_type):
                        self.breaking_changes.append({
                            "type": "type_changed",
                            "path": f"components.schemas.{schema_name}.properties.{field_name}",
                            "message": f"修改字段类型: {schema_name}.{field_name} ({base_type} → {head_type})",
                            "severity": "high"
                        })
                    else:
                        self.non_breaking_changes.append({
                            "type": "type_refined",
                            "path": f"components.schemas.{schema_name}.properties.{field_name}",
                            "message": f"字段类型兼容变更: {schema_name}.{field_name} ({base_type} → {head_type})",
                            "severity": "info"
                        })

    def is_type_compatible(self, base_type: str, head_type: str) -> bool:
        """检查类型变更是否兼容"""
        # string -> string (compatible)
        # number -> integer (compatible, 但可能丢失精度)
        # 其他变更视为不兼容
        if base_type == head_type:
            return True
        if base_type == "number" and head_type == "integer":
            return True
        return False

    def compare(self) -> Dict[str, Any]:
        """执行完整对比"""
        print("🔍 加载基准契约...")
        base_spec = self.load_contract(self.base_path)

        print("🔍 加载目标契约...")
        head_spec = self.load_contract(self.head_path)

        print("🔍 对比API路径...")
        self.compare_paths(base_spec, head_spec)

        print("🔍 对比Schema定义...")
        self.compare_schemas(base_spec, head_spec)

        # 生成报告
        report = {
            "base_contract": str(self.base_path),
            "head_contract": str(self.head_path),
            "breaking_changes_count": len(self.breaking_changes),
            "non_breaking_changes_count": len(self.non_breaking_changes),
            "breaking_changes": self.breaking_changes,
            "non_breaking_changes": self.non_breaking_changes,
            "summary": self.generate_summary(),
        }

        return report

    def generate_summary(self) -> str:
        """生成差异摘要"""
        breaking_count = len(self.breaking_changes)
        non_breaking_count = len(self.non_breaking_changes)

        if breaking_count == 0 and non_breaking_count == 0:
            return "✅ 未检测到任何变更"

        summary_parts = []

        if breaking_count > 0:
            summary_parts.append(f"检测到 {breaking_count} 个破坏性变更")

        if non_breaking_count > 0:
            summary_parts.append(f"{non_breaking_count} 个非破坏性变更")

        return "，".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(
        description="OpenAPI契约差异检测工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 对比两个契约文件
  python compare_contracts.py base.yaml head.yaml -o diff.json

  # 对比Git分支的契约
  python compare_contracts.py --base origin/main --head HEAD
        """
    )

    parser.add_argument(
        "--base",
        required=True,
        help="基准契约文件或Git分支"
    )

    parser.add_argument(
        "--head",
        required=True,
        help="目标契约文件或Git分支"
    )

    parser.add_argument(
        "--output", "-o",
        help="输出JSON报告文件"
    )

    parser.add_argument(
        "--fail-on-breaking",
        action="store_true",
        help="如果检测到破坏性变更则退出码为1"
    )

    args = parser.parse_args()

    # TODO: 支持Git分支对比 (需要实现clone和checkout逻辑)
    # 当前仅支持文件对比
    differ = ContractDiffer(args.base, args.head)

    print("🚀 开始契约差异检测...")
    report = differ.compare()

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ 报告已保存到: {args.output}")

    # 打印摘要
    print("\n" + "="*60)
    print("📊 差异检测摘要")
    print("="*60)
    print(f"基准契约: {report['base_contract']}")
    print(f"目标契约: {report['head_contract']}")
    print(f"破坏性变更: {report['breaking_changes_count']}")
    print(f"非破坏性变更: {report['non_breaking_changes_count']}")
    print(f"摘要: {report['summary']}")
    print("="*60)

    # 返回退出码
    if args.fail_on_breaking and report['breaking_changes_count'] > 0:
        print("\n❌ 检测到破坏性变更，退出码: 1")
        sys.exit(1)
    else:
        print("\n✅ 差异检测完成")
        sys.exit(0)


if __name__ == "__main__":
    main()
