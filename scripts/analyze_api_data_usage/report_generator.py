#!/usr/bin/env python3
"""MyStocks API和Web前端数据使用分析工具（增强版）
支持增量分析、更准确的API调用提取和可视化报告
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class ReportGenerator:
    """生成分析报告"""

    def __init__(self, api_endpoints: List[Dict], frontend_pages: List[Dict], frontend_api_calls: List[Dict]):
        self.api_endpoints = api_endpoints
        self.frontend_pages = frontend_pages
        self.frontend_api_calls = frontend_api_calls

    def generate_json_reports(self, output_dir: Path):
        """生成JSON格式的清单"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # API数据清单
        api_inventory = {
            "generated_at": datetime.now().isoformat(),
            "total_endpoints": len(self.api_endpoints),
            "endpoints": self.api_endpoints,
        }

        with open(output_dir / "api_data_inventory.json", "w", encoding="utf-8") as f:
            json.dump(api_inventory, f, indent=2, ensure_ascii=False)

        print(f"📄 生成 API数据清单: {output_dir / 'api_data_inventory.json'}")

        # Web API调用清单
        web_api_calls = {
            "generated_at": datetime.now().isoformat(),
            "total_pages": len(self.frontend_pages),
            "total_api_calls": len(self.frontend_api_calls),
            "pages": self.frontend_pages,
            "api_calls": self.frontend_api_calls,
        }

        with open(output_dir / "web_api_calls.json", "w", encoding="utf-8") as f:
            json.dump(web_api_calls, f, indent=2, ensure_ascii=False)

        print(f"📄 生成 Web API调用清单: {output_dir / 'web_api_calls.json'}")

    def generate_markdown_report(self, output_file: Path):
        """生成Markdown格式的详细报告"""
        print("📝 生成分析报告...")

        # 构建映射关系
        api_by_path = {ep["path"]: ep for ep in self.api_endpoints}
        api_usage_count = defaultdict(int)
        api_unused = set(api_by_path.keys())

        # 统计API使用情况（从HTTP调用和endpoint字段提取）
        for call in self.frontend_api_calls:
            endpoint = None
            if (call["type"] == "http" and "endpoint" in call) or (
                call["type"] == "api_function" and "endpoint" in call and call["endpoint"]
            ):
                endpoint = call["endpoint"]

            if endpoint:
                # 尝试匹配API路径
                matched_path = self._match_api_path(endpoint, api_by_path.keys())
                if matched_path:
                    api_usage_count[matched_path] += 1
                    if matched_path in api_unused:
                        api_unused.remove(matched_path)

        # 查找前端请求但未实现的API
        frontend_requests = defaultdict(set)
        for call in self.frontend_api_calls:
            if call["type"] == "http" and "endpoint" in call:
                matched_path = self._match_api_path(call["endpoint"], api_by_path.keys())
                if matched_path and matched_path not in api_by_path:
                    frontend_requests[matched_path].add(call["source_file"])

        unimplemented = list(frontend_requests.keys())

        with open(output_file, "w", encoding="utf-8") as f:
            # 写入报告头部
            f.write("# API与Web前端数据使用分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 写入概览
            self._write_overview(f, api_usage_count, unimplemented)

            # 写入API端点统计
            self._write_api_endpoints(f)

            # 写入页面API调用清单
            self._write_page_api_calls(f)

            # 写入数据使用分析
            self._write_data_usage_analysis(f, api_unused, unimplemented)

            # 写入数据库依赖分析
            self._write_database_analysis(f)

            # 写入数据源类型统计
            self._write_source_type_analysis(f)

            # 写入推荐改进
            self._write_recommendations(f)

        print(f"📄 生成分析报告: {output_file}")

    def _match_api_path(self, frontend_path: str, backend_paths: Set[str]) -> str:
        """尝试匹配前端路径到后端API"""
        # 直接匹配
        if frontend_path in backend_paths:
            return frontend_path

        # 去除前导/后的匹配
        normalized = frontend_path.lstrip("/")
        if normalized in backend_paths:
            return normalized

        # 模糊匹配（路径参数替换）
        frontend_parts = frontend_path.split("/")
        for backend_path in backend_paths:
            backend_parts = backend_path.split("/")
            if len(frontend_parts) == len(backend_parts):
                match = True
                for fp, bp in zip(frontend_parts, backend_parts):
                    if fp != bp and not (bp.startswith("{") and bp.endswith("}")):
                        match = False
                        break
                if match:
                    return backend_path

        return None

    def _write_overview(self, f, api_usage_count: Dict[str, int], unimplemented: List[str]):
        """写入概览"""
        f.write("## 概览\n\n")
        f.write(f"- **API端点总数**: {len(self.api_endpoints)}\n")
        f.write(f"- **前端页面总数**: {len(self.frontend_pages)}\n")
        f.write(f"- **API调用总数**: {len(self.frontend_api_calls)}\n")
        f.write(f"- **已使用的API**: {len(api_usage_count)}\n")
        f.write(f"- **未使用的API**: {len(self.api_endpoints) - len(api_usage_count)}\n")
        f.write(f"- **前端请求但未实现的API**: {len(unimplemented)}\n\n")

        # 添加可视化条形图
        f.write("### API使用情况可视化\n\n")
        total = len(self.api_endpoints)

        if total > 0:
            used = len(api_usage_count)
            unused = total - used

            f.write("```\n")
            f.write(f"已使用: {'█' * int(used / total * 50)} {used} ({used / total * 100:.1f}%)\n")
            f.write(f"未使用: {'░' * int(unused / total * 50)} {unused} ({unused / total * 100:.1f}%)\n")
            f.write("```\n\n")
        else:
            f.write("```\n")
            f.write("无API端点数据\n")
            f.write("```\n\n")

    def _write_api_endpoints(self, f):
        """写入API端点统计"""
        f.write("## API端点统计\n\n")
        f.write("### 按HTTP方法分类\n\n")
        f.write("| 方法 | 数量 | 占比 |\n")
        f.write("|------|------|------|\n")

        method_count = defaultdict(int)
        for ep in self.api_endpoints:
            method_count[ep["method"]] += 1

        total = len(self.api_endpoints)
        for method, count in sorted(method_count.items()):
            percentage = (count / total * 100) if total > 0 else 0
            f.write(f"| {method} | {count} | {percentage:.1f}% |\n")

        f.write("\n### API端点详情（按路径分组）\n\n")

        # 按路径分组
        api_by_prefix = defaultdict(list)
        for ep in self.api_endpoints:
            parts = ep["path"].split("/")
            if len(parts) > 1:
                prefix = f"/{parts[1]}"
            else:
                prefix = "其他"
            api_by_prefix[prefix].append(ep)

        for prefix, endpoints in sorted(api_by_prefix.items()):
            f.write(f"#### {prefix} ({len(endpoints)}个端点)\n\n")
            f.write("| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |\n")
            f.write("|------|------|----------|--------|-----------|\n")

            for ep in endpoints:
                f.write(
                    f"| {ep['path']} | {ep['method']} | {ep['return_model']} | {ep['source_type']} | {ep['file']}:{ep['line_number']} |\n",
                )

            f.write("\n")

    def _write_page_api_calls(self, f):
        """写入页面API调用清单"""
        f.write("## 前端页面API调用清单\n\n")

        # 只显示有API调用的页面
        pages_with_calls = [p for p in self.frontend_pages if p["api_calls"]]

        # 按API调用数量排序
        pages_with_calls.sort(key=lambda x: x["api_count"], reverse=True)

        f.write("### Top 10 API调用最多的页面\n\n")
        f.write("| 页面 | 类型 | API调用数 |\n")
        f.write("|------|------|-----------|\n")
        for page in pages_with_calls[:10]:
            f.write(f"| {page['path']} | {page['type']} | {page['api_count']} |\n")

        f.write("\n### 详细API调用清单\n\n")

        for page in pages_with_calls:
            f.write(f"#### {page['path']}\n\n")
            f.write(f"**类型**: {page['type']}  \n")
            f.write(f"**API调用数**: {page['api_count']}  \n\n")

            # 按类型分组显示
            http_calls = [c for c in page["api_calls"] if c["type"] == "http"]
            api_object_calls = [c for c in page["api_calls"] if c["type"] == "api_object"]
            other_calls = [c for c in page["api_calls"] if c["type"] not in ["http", "api_object"]]

            if http_calls:
                f.write("##### HTTP调用\n\n")
                f.write("| 方法 | 端点 | 行号 |\n")
                f.write("|------|------|------|\n")
                for call in http_calls[:10]:  # 限制显示数量
                    f.write(f"| {call['method']} | {call['endpoint']} | {call['line']} |\n")
                if len(http_calls) > 10:
                    f.write(f"| ... | 还有 {len(http_calls) - 10} 个 | ... |\n")
                f.write("\n")

            if api_object_calls:
                f.write("##### API对象调用\n\n")
                f.write("| API对象 | 方法 | 行号 |\n")
                f.write("|---------|------|------|\n")
                for call in api_object_calls[:10]:
                    f.write(f"| {call['api_name']} | {call['method']} | {call['line']} |\n")
                if len(api_object_calls) > 10:
                    f.write(f"| ... | 还有 {len(api_object_calls) - 10} 个 | ... |\n")
                f.write("\n")

            if other_calls:
                f.write("##### 其他调用\n\n")
                f.write(f"共 {len(other_calls)} 个其他调用（类型: {[c['type'] for c in other_calls[:5]]}...）\n\n")

    def _write_data_usage_analysis(self, f, api_unused: Set[str], unimplemented: List[str]):
        """写入数据使用分析"""
        f.write("## 数据使用分析\n\n")

        # 未使用的API
        f.write("### API返回但前端未使用\n\n")
        if api_unused:
            f.write(f"共 {len(api_unused)} 个API端点未被前端使用：\n\n")
            f.write("| 路径 | 方法 | 返回模型 | 文件 |\n")
            f.write("|------|------|----------|------|\n")

            for path in sorted(api_unused)[:50]:  # 限制显示数量
                ep = next((e for e in self.api_endpoints if e["path"] == path), None)
                if ep:
                    f.write(f"| {ep['path']} | {ep['method']} | {ep['return_model']} | {ep['file']} |\n")

            if len(api_unused) > 50:
                f.write(f"| ... | ... | ... | ... (还有 {len(api_unused) - 50} 个) |\n")
        else:
            f.write("✅ 所有API端点都已被前端使用\n\n")

        f.write("\n### 前端请求但API未实现\n\n")
        if unimplemented:
            f.write(f"共 {len(unimplemented)} 个端点前端请求但后端未实现：\n\n")
            f.write("| 端点 | 请求页面数 |\n")
            f.write("|------|-----------|\n")

            for endpoint in sorted(unimplemented)[:20]:  # 限制显示数量
                pages = len(frontend_requests.get(endpoint, set()))
                f.write(f"| {endpoint} | {pages} |\n")

            if len(unimplemented) > 20:
                f.write(f"| ... | ... (还有 {len(unimplemented) - 20} 个) |\n")
        else:
            f.write("✅ 所有前端请求的API都已实现\n\n")

    def _write_database_analysis(self, f):
        """写入数据库依赖分析"""
        f.write("## 数据库依赖分析\n\n")

        # 统计数据库表使用
        db_tables = defaultdict(list)
        for ep in self.api_endpoints:
            for table in ep["db_dependencies"]:
                db_tables[table].append(ep["path"])

        if db_tables:
            f.write("### API使用的数据库表\n\n")
            f.write("| 表名 | 被API端点使用次数 | 端点示例 |\n")
            f.write("|------|------------------|----------|\n")

            for table, endpoints in sorted(db_tables.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"| {table} | {len(endpoints)} | {', '.join(endpoints[:3])} |\n")
        else:
            f.write("ℹ️  未检测到明确的数据库表依赖\n\n")

    def _write_source_type_analysis(self, f):
        """写入数据源类型统计"""
        f.write("## 数据源类型统计\n\n")
        f.write("| 数据源类型 | API数量 | 占比 |\n")
        f.write("|-----------|---------|------|\n")

        source_count = defaultdict(int)
        for ep in self.api_endpoints:
            source_count[ep["source_type"]] += 1

        total = len(self.api_endpoints)
        for source_type, count in sorted(source_count.items()):
            percentage = (count / total * 100) if total > 0 else 0
            f.write(f"| {source_type} | {count} | {percentage:.1f}% |\n")

        f.write("\n### Mock数据API清单\n\n")
        mock_apis = [ep for ep in self.api_endpoints if ep["source_type"] == "mock"]
        if mock_apis:
            f.write("| 路径 | 方法 | 文件 |\n")
            f.write("|------|------|------|\n")
            for ep in mock_apis:
                f.write(f"| {ep['path']} | {ep['method']} | {ep['file']} |\n")
        else:
            f.write("✅ 没有使用Mock数据的API\n\n")

    def _write_recommendations(self, f):
        """写入推荐改进"""
        f.write("## 推荐改进\n\n")

        # 统计数据
        api_by_path = {ep["path"]: ep for ep in self.api_endpoints}
        api_usage_count = defaultdict(int)
        for call in self.frontend_api_calls:
            if call["type"] == "http" and "endpoint" in call:
                matched = self._match_api_path(call["endpoint"], api_by_path.keys())
                if matched:
                    api_usage_count[matched] += 1

        api_unused = set(api_by_path.keys()) - set(api_usage_count.keys())

        recommendations = []

        # 1. 清理未使用的API
        if len(api_unused) > 10:
            recommendations.append(
                {
                    "priority": "高",
                    "category": "代码清理",
                    "description": f"有 {len(api_unused)} 个API端点未被前端使用，建议评估是否需要删除或标记为deprecated",
                },
            )

        # 2. Mock数据替换
        mock_count = sum(1 for ep in self.api_endpoints if ep["source_type"] == "mock")
        if mock_count > 0:
            recommendations.append(
                {
                    "priority": "中",
                    "category": "数据源",
                    "description": f"有 {mock_count} 个API仍在使用Mock数据，建议替换为真实数据源",
                },
            )

        # 3. API调用优化
        if len(self.frontend_api_calls) > 2000:
            recommendations.append(
                {
                    "priority": "低",
                    "category": "性能优化",
                    "description": f"前端共 {len(self.frontend_api_calls)} 个API调用，建议分析是否有重复或冗余调用",
                },
            )

        if recommendations:
            f.write("| 优先级 | 类别 | 建议 |\n")
            f.write("|--------|------|------|\n")
            for rec in recommendations:
                f.write(f"| {rec['priority']} | {rec['category']} | {rec['description']} |\n")
        else:
            f.write("✅ 未发现明显改进点\n\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks API与Web前端数据使用分析工具")
    parser.add_argument("--incremental", "-i", action="store_true", help="增量分析模式，只分析修改的文件")
    args = parser.parse_args()

    print("=" * 60)
    print("MyStocks API与Web前端数据使用分析工具")
    if args.incremental:
        print("模式: 增量分析")
    print("=" * 60)

    # 路径配置
    backend_dir = Path("web/backend/app/api")
    frontend_dir = Path("web/frontend/src")
    output_dir = Path("docs/reports")
    report_file = output_dir / "API_WEB_DATA_USAGE_REPORT.md"

    # 检查目录是否存在
    if not backend_dir.exists():
        print(f"❌ 后端API目录不存在: {backend_dir}")
        return

    if not frontend_dir.exists():
        print(f"❌ 前端目录不存在: {frontend_dir}")
        return

    # 分析API
    api_analyzer = APIAnalyzer(str(backend_dir))
    api_endpoints = api_analyzer.analyze(incremental=args.incremental)

    # 分析前端
    frontend_analyzer = FrontendAnalyzer(str(frontend_dir))
    frontend_pages, frontend_api_calls = frontend_analyzer.analyze(incremental=args.incremental)

    # 生成报告
    report_generator = ReportGenerator(api_endpoints, frontend_pages, frontend_api_calls)
    report_generator.generate_json_reports(output_dir)
    report_generator.generate_markdown_report(report_file)

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"   - API端点: {len(api_endpoints)}")
    print(f"   - 前端页面: {len(frontend_pages)}")
    print(f"   - API调用: {len(frontend_api_calls)}")
    print(f"\n   报告位置: {report_file}")
    print(f"   JSON清单: {output_dir / 'api_data_inventory.json'}")
    print(f"   JSON清单: {output_dir / 'web_api_calls.json'}")
    if args.incremental:
        print("\n💡 提示: 使用 --incremental 参数可以加速后续分析")
    print("=" * 60)
