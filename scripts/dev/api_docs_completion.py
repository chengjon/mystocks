#!/usr/bin/env python3
"""
API文档完整性检查和补充工具
API Documentation Completion Tool

Phase 6-3: 补充API文档完整性

功能特性:
- 扫描所有API端点
- 检查文档完整性
- 生成缺失的API文档
- 更新OpenAPI规范
- 创建API使用示例
- 生成文档覆盖率报告

Author: Claude Code
Date: 2025-11-13
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import ast
from dataclasses import dataclass


@dataclass
class APIEndpoint:
    """API端点信息"""

    file_path: str
    function_name: str
    http_method: str
    path: str
    summary: Optional[str]
    description: Optional[str]
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Any]
    has_docstring: bool
    docstring_quality: str  # excellent/good/fair/poor/missing


@dataclass
class DocumentationCoverage:
    """文档覆盖率统计"""

    total_endpoints: int
    documented_endpoints: int
    partially_documented: int
    undocumented: int
    coverage_percentage: float
    missing_endpoints: List[str]
    quality_distribution: Dict[str, int]


class APIDocumentationAnalyzer:
    """API文档分析器"""

    def __init__(self, api_directory: str):
        """
        初始化分析器

        Args:
            api_directory: API目录路径
        """
        self.api_directory = Path(api_directory)
        self.endpoints: List[APIEndpoint] = []
        self.coverage_stats = None

    def scan_api_endpoints(self) -> List[APIEndpoint]:
        """
        扫描所有API端点

        Returns:
            API端点列表
        """
        print("🔍 扫描API端点...")

        for file_path in self.api_directory.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                endpoints = self._extract_endpoints_from_file(file_path)
                self.endpoints.extend(endpoints)
            except Exception as e:
                print(f"⚠️ 扫描文件失败: {file_path} - {e}")

        print(f"✅ 发现 {len(self.endpoints)} 个API端点")
        return self.endpoints

    def _extract_endpoints_from_file(self, file_path: Path) -> List[APIEndpoint]:
        """从文件中提取API端点"""
        endpoints = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 检查普通函数和异步函数
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    endpoint = self._analyze_function(node, file_path, content)
                    if endpoint:
                        endpoints.append(endpoint)

        except Exception as e:
            print(f"⚠️ 解析文件失败: {file_path} - {e}")

        return endpoints

    def _analyze_function(
        self, node: ast.AST, file_path: Path, content: str
    ) -> Optional[APIEndpoint]:
        """分析函数，提取API信息"""
        # 检查是否是API路由函数
        if not self._is_api_function(node):
            return None

        # 提取函数信息
        http_method, path = self._extract_route_info(node, content)
        if not http_method or not path:
            return None

        # 分析文档字符串
        docstring_info = self._analyze_docstring(node)

        # 提取参数信息
        parameters = self._extract_parameters(node)

        # 提取响应信息
        responses = self._extract_responses(node, content)

        return APIEndpoint(
            file_path=str(file_path.relative_to(self.api_directory)),
            function_name=node.name,
            http_method=http_method,
            path=path,
            summary=docstring_info["summary"],
            description=docstring_info["description"],
            parameters=parameters,
            responses=responses,
            has_docstring=docstring_info["has_docstring"],
            docstring_quality=docstring_info["quality"],
        )

    def _is_api_function(self, node: ast.FunctionDef) -> bool:
        """检查是否是API路由函数"""
        # 查找@router装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # 检查 @router.get(), @router.post() 等
                    if decorator.func.attr in ["get", "post", "put", "delete", "patch"]:
                        # 检查是否是router实例的调用
                        if isinstance(decorator.func.value, ast.Name):
                            if decorator.func.value.id == "router":
                                return True
                elif isinstance(decorator.func, ast.Name):
                    if decorator.func.id == "router":
                        return True
        return False

    def _extract_route_info(
        self, node: ast.FunctionDef, content: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """提取路由信息"""
        http_method = None
        path = None

        # 查找装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # 检查 @router.get(...) 模式
                    method = decorator.func.attr
                    if method in ["get", "post", "put", "delete", "patch"]:
                        # 检查是否是router实例
                        if isinstance(decorator.func.value, ast.Name):
                            if decorator.func.value.id == "router":
                                http_method = method.upper()
                                if decorator.args:
                                    if isinstance(decorator.args[0], ast.Constant):
                                        path = decorator.args[0].value
                                break

        return http_method, path

    def _analyze_docstring(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """分析文档字符串"""
        if (
            not node.body
            or not isinstance(node.body[0], ast.Expr)
            or not isinstance(node.body[0].value, ast.Constant)
        ):
            return {
                "has_docstring": False,
                "summary": None,
                "description": None,
                "quality": "missing",
            }

        docstring = node.body[0].value.value

        # 简单分析文档字符串质量
        lines = docstring.split("\n")
        summary = lines[0].strip() if lines else None

        # 判断质量
        if not docstring.strip():
            quality = "missing"
        elif len(docstring) < 50:
            quality = "poor"
        elif len(docstring) < 200:
            quality = "fair"
        elif len(docstring) < 500:
            quality = "good"
        else:
            quality = "excellent"

        return {
            "has_docstring": bool(docstring.strip()),
            "summary": summary,
            "description": docstring,
            "quality": quality,
        }

    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """提取参数信息"""
        parameters = []

        for arg in node.args.args:
            if arg.arg in ["self", "cls"]:
                continue

            param_info = {
                "name": arg.arg,
                "type": "unknown",
                "required": True,
                "description": None,
            }

            # 简单的类型推断
            if hasattr(node, "returns") and node.returns:
                if isinstance(node.returns, ast.Name):
                    param_info["type"] = node.returns.id

            parameters.append(param_info)

        return parameters

    def _extract_responses(self, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """提取响应信息"""
        # 这是一个简化的实现，实际中可能需要更复杂的分析
        return {"200": {"description": "Success"}}

    def calculate_coverage(self) -> DocumentationCoverage:
        """计算文档覆盖率"""
        # 创建默认的覆盖统计
        default_coverage = DocumentationCoverage(
            total_endpoints=0,
            documented_endpoints=0,
            partially_documented=0,
            undocumented=0,
            coverage_percentage=0.0,
            missing_endpoints=[],
            quality_distribution={},
        )

        if not self.endpoints:
            self.coverage_stats = default_coverage
            return default_coverage

        documented = sum(1 for e in self.endpoints if e.has_docstring)
        partially = sum(
            1
            for e in self.endpoints
            if e.has_docstring and e.docstring_quality in ["poor", "fair"]
        )
        undocumented = len(self.endpoints) - documented
        coverage_percentage = (documented / len(self.endpoints)) * 100

        # 质量分布统计
        quality_dist = {}
        for endpoint in self.endpoints:
            quality = endpoint.docstring_quality
            quality_dist[quality] = quality_dist.get(quality, 0) + 1

        # 缺失文档的端点
        missing_endpoints = [
            f"{e.http_method} {e.path} ({e.function_name})"
            for e in self.endpoints
            if not e.has_docstring
        ]

        self.coverage_stats = DocumentationCoverage(
            total_endpoints=len(self.endpoints),
            documented_endpoints=documented,
            partially_documented=partially,
            undocumented=undocumented,
            coverage_percentage=coverage_percentage,
            missing_endpoints=missing_endpoints,
            quality_distribution=quality_dist,
        )

        return self.coverage_stats

    def generate_coverage_report(self) -> str:
        """生成覆盖率报告"""
        if not self.coverage_stats:
            self.calculate_coverage()

        stats = self.coverage_stats

        report = f"""
# API文档覆盖率报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 总体统计

- **总端点数**: {stats.total_endpoints}
- **已文档化**: {stats.documented_endpoints} ({stats.coverage_percentage:.1f}%)
- **部分文档化**: {stats.partially_documented}
- **未文档化**: {stats.undocumented}

## 📈 文档质量分布

"""

        for quality, count in stats.quality_distribution.items():
            percentage = (count / stats.total_endpoints) * 100
            status_icon = {
                "excellent": "🟢",
                "good": "🟡",
                "fair": "🟠",
                "poor": "🔴",
                "missing": "⚫",
            }.get(quality, "⚪")

            report += (
                f"- {status_icon} **{quality.title()}**: {count} ({percentage:.1f}%)\n"
            )

        if stats.missing_endpoints:
            report += "\n## ❌ 缺失文档的端点\n\n"
            for endpoint in stats.missing_endpoints[:10]:  # 只显示前10个
                report += f"- `{endpoint}`\n"

            if len(stats.missing_endpoints) > 10:
                report += f"- ... 还有 {len(stats.missing_endpoints) - 10} 个端点\n"

        return report

    def identify_documentation_gaps(self) -> Dict[str, List[str]]:
        """识别文档缺口"""
        gaps = {
            "missing_docstrings": [],
            "poor_quality": [],
            "incomplete_parameters": [],
            "missing_responses": [],
            "inconsistent_style": [],
        }

        for endpoint in self.endpoints:
            # 缺失文档字符串
            if not endpoint.has_docstring:
                gaps["missing_docstrings"].append(
                    f"{endpoint.http_method} {endpoint.path}"
                )

            # 文档质量差
            elif endpoint.docstring_quality in ["poor", "missing"]:
                gaps["poor_quality"].append(
                    f"{endpoint.http_method} {endpoint.path} (质量: {endpoint.docstring_quality})"
                )

            # 参数信息不完整
            if endpoint.parameters and not all(
                p.get("description") for p in endpoint.parameters
            ):
                gaps["incomplete_parameters"].append(
                    f"{endpoint.http_method} {endpoint.path}"
                )

        return gaps

    def generate_missing_docs(self, output_dir: str):
        """生成缺失的文档"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        gaps = self.identify_documentation_gaps()

        # 生成缺失文档的模板
        if gaps["missing_docstrings"]:
            missing_docs_file = output_path / "missing_docstrings.md"
            with open(missing_docs_file, "w", encoding="utf-8") as f:
                f.write("# 缺失文档的API端点\n\n")
                f.write("以下端点需要添加文档字符串：\n\n")

                for endpoint_path in gaps["missing_docstrings"]:
                    f.write(f"## {endpoint_path}\n\n")
                    f.write("```python\n")
                    f.write(
                        f'@router.{endpoint_path.split()[0].lower()}("{endpoint_path.split()[1]}")\n'
                    )
                    f.write("async def some_function():\n")
                    f.write('    """\n')
                    f.write("    TODO: 添加函数文档字符串\n\n")
                    f.write("    Returns:\n")
                    f.write("        TODO: 描述返回值\n")
                    f.write('    """\n')
                    f.write("    pass\n")
                    f.write("```\n\n")

            print(f"📝 已生成缺失文档模板: {missing_docs_file}")


def main():
    """主函数"""
    print("🔧 API文档完整性检查工具")
    print("=" * 50)

    # 初始化分析器
    api_dir = "/opt/claude/mystocks_spec/web/backend/app/api"
    analyzer = APIDocumentationAnalyzer(api_dir)

    # 扫描端点
    endpoints = analyzer.scan_api_endpoints()

    # 计算覆盖率
    coverage = analyzer.calculate_coverage()

    # 生成报告
    report = analyzer.generate_coverage_report()
    print(report)

    # 识别缺口
    gaps = analyzer.identify_documentation_gaps()

    print("\n📋 文档缺口分析:")
    for gap_type, items in gaps.items():
        if items:
            print(f"  {gap_type}: {len(items)} 个问题")

    # 生成补充文档
    output_dir = "/opt/claude/mystocks_spec/var/log/api_docs_gaps"
    analyzer.generate_missing_docs(output_dir)

    # 保存详细结果
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_endpoints": len(endpoints),
        "coverage": {
            "total_endpoints": coverage.total_endpoints,
            "documented_endpoints": coverage.documented_endpoints,
            "coverage_percentage": coverage.coverage_percentage,
            "quality_distribution": coverage.quality_distribution,
        },
        "endpoints": [
            {
                "file": e.file_path,
                "function": e.function_name,
                "method": e.http_method,
                "path": e.path,
                "has_docstring": e.has_docstring,
                "quality": e.docstring_quality,
            }
            for e in endpoints
        ],
        "gaps": gaps,
    }

    results_file = f"/opt/claude/mystocks_spec/var/log/api_docs_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 详细分析结果已保存: {results_file}")

    # 返回结果
    return coverage.coverage_percentage


if __name__ == "__main__":
    main()
