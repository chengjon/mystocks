#!/usr/bin/env python3
"""
P0 API实现状态分析脚本
检查所有P0 API的实现质量、测试覆盖率和改进建议
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class APIAnalyzer:
    """API分析器"""

    def __init__(self, backend_dir: Path):
        self.backend_dir = backend_dir
        self.api_files = self._find_api_files()
        self.analysis_results = defaultdict(dict)

    def _find_api_files(self) -> List[Path]:
        """查找所有API文件"""
        api_dir = self.backend_dir / "app" / "api"
        files = []

        # 查找app/api/下的所有.py文件
        if api_dir.exists():
            files.extend(api_dir.glob("*.py"))
            files.extend(api_dir.glob("**/*.py"))

        # 添加trade模块
        trade_api = api_dir / "trade"
        if trade_api.exists():
            files.extend(trade_api.glob("*.py"))

        return [f for f in files if f.name != "__init__.py" and not f.name.startswith("_")]

    def analyze_api_file(self, filepath: Path) -> Dict:
        """分析单个API文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            analysis = {
                "file": str(filepath.relative_to(self.backend_dir)),
                "routes": [],
                "has_pydantic": False,
                "has_service": False,
                "has_error_handling": False,
                "has_validation": False,
                "has_cache": False,
                "code_lines": len(content.split('\n')),
                "implementation_quality": "unknown",
            }

            # 检查导入
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])

            # 检查关键组件
            analysis["has_pydantic"] = any("pydantic" in imp for imp in imports)
            analysis["has_service"] = any("service" in imp for imp in imports)
            analysis["has_validation"] = any("BaseModel" in content or "Field" in content for _ in [True])
            analysis["has_error_handling"] = "HTTPException" in content or "create_error_response" in content
            analysis["has_cache"] = any("cache" in imp for imp in imports)

            # 检查路由实现
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否是路由函数
                    is_route = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if hasattr(decorator.func, 'attr'):
                                if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                    is_route = True

                    if is_route:
                        route_info = {
                            "name": node.name,
                            "has_logic": len(node.body) > 5,  # 超过5行说明有逻辑
                            "has_try_except": any(isinstance(n, ast.Try) for n in node.body),
                            "has_return": any(isinstance(n, ast.Return) for n in node.body),
                        }
                        analysis["routes"].append(route_info)

            # 评估实现质量
            implemented_routes = sum(1 for r in analysis["routes"] if r["has_logic"])
            total_routes = len(analysis["routes"])

            if total_routes == 0:
                analysis["implementation_quality"] = "no_routes"
            elif implemented_routes == total_routes:
                if analysis["has_service"] and analysis["has_error_handling"]:
                    analysis["implementation_quality"] = "production_ready"
                else:
                    analysis["implementation_quality"] = "basic"
            elif implemented_routes > 0:
                analysis["implementation_quality"] = "partial"
            else:
                analysis["implementation_quality"] = "stub"

            return analysis

        except Exception as e:
            return {
                "file": str(filepath.relative_to(self.backend_dir)),
                "error": str(e),
                "implementation_quality": "error",
            }

    def analyze_all_apis(self) -> Dict:
        """分析所有API"""
        print("🔍 分析P0 API实现状态...\n")

        results = {}
        for api_file in self.api_files:
            result = self.analyze_api_file(api_file)
            module_name = api_file.stem
            results[module_name] = result

        return results

    def generate_report(self) -> Dict:
        """生成综合报告"""
        results = self.analyze_all_apis()

        # 统计
        quality_stats = defaultdict(int)
        module_stats = []

        for module, analysis in results.items():
            if "error" not in analysis:
                quality = analysis["implementation_quality"]
                quality_stats[quality] += 1

                module_stats.append({
                    "module": module,
                    "quality": quality,
                    "routes": len(analysis["routes"]),
                    "has_service": analysis["has_service"],
                    "has_validation": analysis["has_validation"],
                    "has_error_handling": analysis["has_error_handling"],
                    "code_lines": analysis["code_lines"],
                })

        # 按质量分组
        production_ready = [m for m in module_stats if m["quality"] == "production_ready"]
        basic = [m for m in module_stats if m["quality"] == "basic"]
        partial = [m for m in module_stats if m["quality"] == "partial"]
        stub = [m for m in module_stats if m["quality"] == "stub"]

        report = {
            "total_modules": len(module_stats),
            "quality_distribution": dict(quality_stats),
            "production_ready_modules": production_ready,
            "basic_modules": basic,
            "partial_modules": partial,
            "stub_modules": stub,
            "detailed_results": results,
        }

        return report


def main():
    """主函数"""
    backend_dir = Path(".")  # 当前目录

    if not backend_dir.exists():
        print(f"❌ Backend目录不存在: {backend_dir}")
        return

    analyzer = APIAnalyzer(backend_dir)
    report = analyzer.generate_report()

    print("=" * 70)
    print("📊 P0 API实现状态报告")
    print("=" * 70)

    print(f"\n总模块数: {report['total_modules']}")
    print(f"\n实现质量分布:")
    for quality, count in report['quality_distribution'].items():
        emoji = {
            "production_ready": "✅",
            "basic": "🟡",
            "partial": "🟠",
            "stub": "🔴",
            "no_routes": "⚪",
        }.get(quality, "❓")
        print(f"  {emoji} {quality}: {count} 个")

    print(f"\n✅ 生产就绪模块 ({len(report['production_ready_modules'])}个):")
    for m in report['production_ready_modules'][:5]:
        print(f"  - {m['module']:30} {m['routes']:2} 路由  {m['code_lines']:4} 行")
    if len(report['production_ready_modules']) > 5:
        print(f"  ... 还有 {len(report['production_ready_modules']) - 5} 个")

    print(f"\n🟡 基础实现模块 ({len(report['basic_modules'])}个):")
    for m in report['basic_modules'][:5]:
        print(f"  - {m['module']:30} {m['routes']:2} 路由")
    if len(report['basic_modules']) > 5:
        print(f"  ... 还有 {len(report['basic_modules']) - 5} 个")

    print(f"\n🟠 部分实现模块 ({len(report['partial_modules'])}个):")
    for m in report['partial_modules'][:5]:
        print(f"  - {m['module']:30} {m['routes']:2} 路由")
    if len(report['partial_modules']) > 5:
        print(f"  ... 还有 {len(report['partial_modules']) - 5} 个")

    print(f"\n🔴 空框架模块 ({len(report['stub_modules'])}个):")
    for m in report['stub_modules']:
        print(f"  - {m['module']:30} 需要实现")

    print("\n" + "=" * 70)
    print("💡 改进建议:")
    print("=" * 70)

    if report['stub_modules']:
        print("\n1. 优先实现空框架模块:")
        for m in report['stub_modules']:
            print(f"   - {m['module']}: 需要添加路由和业务逻辑")

    if report['partial_modules']:
        print("\n2. 完善部分实现模块:")
        for m in report['partial_modules']:
            print(f"   - {m['module']}: 需要完成未实现的路由")

    if report['basic_modules']:
        print("\n3. 增强基础实现模块:")
        for m in report['basic_modules']:
            if not m['has_service']:
                print(f"   - {m['module']}: 需要添加service层调用")
            if not m['has_validation']:
                print(f"   - {m['module']}: 需要增强数据验证")

    # 保存报告
    report_file = Path("web/backend/P0_API_STATUS_REPORT.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n📁 详细报告已保存: {report_file}")


if __name__ == "__main__":
    main()
