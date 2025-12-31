#!/usr/bin/env python3
"""
从OpenAPI JSON文档解析API端点并生成catalog.yaml和catalog.md
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class Priority(Enum):
    """API优先级"""
    P0 = "P0"  # 核心业务API（30个）
    P1 = "P1"  # 重要业务API（85个）
    P2 = "P2"  # 辅助功能API（94个）


@dataclass
class APIEndpoint:
    """API端点数据类"""
    api_id: str
    module: str
    path: str
    method: str
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    priority: Priority = Priority.P2
    request_params: Dict[str, Any] = field(default_factory=dict)
    response_code: int = 200
    response_data: Dict[str, Any] = field(default_factory=dict)


def determine_priority(path: str, tags: List[str], method: str) -> Priority:
    """确定API优先级"""
    # P0: 核心业务API
    p0_patterns = [
        (r"^/api/market/.*", ["market"]),
        (r"^/api/strategy/.*", ["strategy"]),
        (r"^/api/trade/.*", ["trade"]),
        (r"^/api/v1/auth/login.*", ["auth"]),
        (r"^/api/market$", ["market"]),
        (r"^/api/data/.*", ["data"]),
    ]

    # P1: 重要业务API
    p1_patterns = [
        (r"^/api/backtest.*", ["strategy", "backtest"]),
        (r"^/api/risk.*", ["risk"]),
        (r"^/api/indicators/.*", ["indicators"]),
        (r"^/api/technical.*", ["technical-analysis", "technical"]),
        (r"^/api/watchlist.*", ["watchlist"]),
        (r"^/api/stock-search.*", ["stock-search"]),
        (r"^/api/tradingview.*", ["tradingview"]),
        (r"^/api/notification.*", ["notification"]),
        (r"^/api/dashboard.*", ["dashboard"]),
        (r"^/api/data-quality.*", ["data-quality"]),
        (r"^/api/cache.*", ["cache"]),
    ]

    for pattern, pattern_tags in p0_patterns:
        if re.match(pattern, path) or any(tag in pattern_tags for tag in tags):
            return Priority.P0

    for pattern, pattern_tags in p1_patterns:
        if re.match(pattern, path) or any(tag in pattern_tags for tag in tags):
            return Priority.P1

    return Priority.P2


def generate_api_id(path: str, method: str, tags: List[str]) -> str:
    """生成唯一API ID"""
    clean_path = path.strip("/").replace("/", "_").replace("-", "_").replace("{", "").replace("}", "")
    if not clean_path:
        clean_path = "root"

    module = tags[0] if tags else "api"
    module = module.replace("-", "_").replace(" ", "_")

    return f"{module}_{method.lower()}_{clean_path}"


def parse_openapi_json(json_file: Path) -> List[APIEndpoint]:
    """解析OpenAPI JSON文件"""
    print(f"📖 读取OpenAPI文档: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        openapi_data = json.load(f)

    endpoints: List[APIEndpoint] = []

    # 遍历所有路径
    paths = openapi_data.get("paths", {})
    print(f"✓ 发现 {len(paths)} 个路径")

    for path, path_item in paths.items():
        for method, method_item in path_item.items():
            if method.lower() in ["get", "post", "put", "patch", "delete", "options", "head"]:
                # 提取信息
                summary = method_item.get("summary", "")
                description = method_item.get("description", "")
                tags = method_item.get("tags", [])

                # 确定优先级
                priority = determine_priority(path, tags, method)

                # 生成API ID
                api_id = generate_api_id(path, method, tags)

                # 提取请求参数
                request_params = {}
                for param in method_item.get("parameters", []):
                    param_name = param.get("name", "")
                    request_params[param_name] = {
                        "in": param.get("in", "query"),
                        "required": param.get("required", False),
                        "description": param.get("description", ""),
                    }

                # 提取请求体
                if "requestBody" in method_item:
                    request_body = method_item["requestBody"]
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        request_params["body"] = {
                            "in": "body",
                            "required": request_body.get("required", False),
                            "content_type": "application/json",
                        }

                # 获取模块名
                module = tags[0] if tags else "api"

                # 创建端点
                endpoint = APIEndpoint(
                    api_id=api_id,
                    module=module,
                    path=path,
                    method=method.upper(),
                    summary=summary,
                    description=description,
                    tags=tags,
                    priority=priority,
                    request_params=request_params,
                )
                endpoints.append(endpoint)

    print(f"✓ 解析完成，共 {len(endpoints)} 个API端点")
    return endpoints


def generate_catalog_yaml(endpoints: List[APIEndpoint], output_path: Path):
    """生成catalog.yaml"""
    import yaml

    catalog = {
        "version": "1.0.0",
        "generated_at": "2025-12-30",
        "generated_from": "openapi_json",
        "total_apis": len(endpoints),
        "modules": {},
        "apis": [],
    }

    # 按模块分组
    module_groups: Dict[str, List[APIEndpoint]] = {}
    for endpoint in endpoints:
        if endpoint.module not in module_groups:
            module_groups[endpoint.module] = []
        module_groups[endpoint.module].append(endpoint)

    # 添加模块信息
    for module, eps in module_groups.items():
        p0_count = sum(1 for e in eps if e.priority == Priority.P0)
        p1_count = sum(1 for e in eps if e.priority == Priority.P1)
        p2_count = sum(1 for e in eps if e.priority == Priority.P2)

        catalog["modules"][module] = {
            "name": module,
            "total_endpoints": len(eps),
            "priority_distribution": {
                "P0": p0_count,
                "P1": p1_count,
                "P2": p2_count,
            },
        }

    # 添加所有API
    for endpoint in endpoints:
        api_data = {
            "api_id": endpoint.api_id,
            "module": endpoint.module,
            "path": endpoint.path,
            "method": endpoint.method,
            "summary": endpoint.summary,
            "description": endpoint.description,
            "priority": endpoint.priority.value,
            "tags": endpoint.tags,
        }
        if endpoint.request_params:
            api_data["request_params"] = endpoint.request_params
        catalog["apis"].append(api_data)

    # 写入文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(catalog, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✓ 生成 {output_path}")


def generate_catalog_md(endpoints: List[APIEndpoint], output_path: Path):
    """生成catalog.md（人类可读的API文档）"""
    # 按模块和优先级分组
    module_groups: Dict[str, Dict[Priority, List[APIEndpoint]]] = {}
    for endpoint in endpoints:
        if endpoint.module not in module_groups:
            module_groups[endpoint.module] = {Priority.P0: [], Priority.P1: [], Priority.P2: []}
        module_groups[endpoint.module][endpoint.priority].append(endpoint)

    # 排序模块
    sorted_modules = sorted(module_groups.keys())

    # 生成Markdown
    lines = [
        "# MyStocks API 目录",
        "",
        f"**生成时间**: 2025-12-30",
        f"**数据来源**: FastAPI OpenAPI (localhost:8000)",
        f"**API总数**: {len(endpoints)}",
        "",
        "## 目录",
        "",
    ]

    # 添加目录
    for module in sorted_modules:
        lines.append(f"- [{module}](#{module.replace('_', '-')})")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 为每个模块生成详细内容
    total_p0 = 0
    total_p1 = 0
    total_p2 = 0

    for module in sorted_modules:
        lines.append(f"## {module}")
        lines.append("")
        p0_eps = module_groups[module][Priority.P0]
        p1_eps = module_groups[module][Priority.P1]
        p2_eps = module_groups[module][Priority.P2]

        if p0_eps:
            lines.append("### P0 - 核心业务API")
            lines.append("")
            for ep in sorted(p0_eps, key=lambda e: (e.method, e.path)):
                lines.append(f"#### {ep.method} {ep.path}")
                lines.append("")
                if ep.summary:
                    lines.append(f"**描述**: {ep.summary}")
                    lines.append("")
                lines.append(f"- **API ID**: `{ep.api_id}`")
                lines.append(f"- **标签**: {', '.join(ep.tags)}")
                if ep.request_params:
                    lines.append(f"- **参数**: {len(ep.request_params)} 个")
                lines.append("")
                total_p0 += 1

        if p1_eps:
            lines.append("### P1 - 重要业务API")
            lines.append("")
            for ep in sorted(p1_eps, key=lambda e: (e.method, e.path)):
                lines.append(f"#### {ep.method} {ep.path}")
                lines.append("")
                if ep.summary:
                    lines.append(f"**描述**: {ep.summary}")
                    lines.append("")
                lines.append(f"- **API ID**: `{ep.api_id}`")
                lines.append(f"- **标签**: {', '.join(ep.tags)}")
                if ep.request_params:
                    lines.append(f"- **参数**: {len(ep.request_params)} 个")
                lines.append("")
                total_p1 += 1

        if p2_eps:
            lines.append("### P2 - 辅助功能API")
            lines.append("")
            for ep in sorted(p2_eps, key=lambda e: (e.method, e.path)):
                lines.append(f"#### {ep.method} {ep.path}")
                lines.append("")
                if ep.summary:
                    lines.append(f"**描述**: {ep.summary}")
                    lines.append("")
                lines.append(f"- **API ID**: `{ep.api_id}`")
                lines.append(f"- **标签**: {', '.join(ep.tags)}")
                if ep.request_params:
                    lines.append(f"- **参数**: {len(ep.request_params)} 个")
                lines.append("")
                total_p2 += 1

        lines.append("---")
        lines.append("")

    # 添加统计摘要
    lines.insert(7, "")
    lines.insert(7, f"- **P0**: {total_p0} 个（核心业务）")
    lines.insert(7, f"- **P1**: {total_p1} 个（重要业务）")
    lines.insert(7, f"- **P2**: {total_p2} 个（辅助功能）")
    lines.insert(7, "## 优先级分布")

    # 写入文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✓ 生成 {output_path}")


def main():
    """主函数"""
    # 定义路径
    json_file = Path("/tmp/openapi.json")
    docs_dir = Path("docs/api")

    if not json_file.exists():
        print(f"❌ OpenAPI文件不存在: {json_file}")
        print("请先运行: curl -s http://localhost:8000/openapi.json > /tmp/openapi.json")
        return

    # 解析OpenAPI
    endpoints = parse_openapi_json(json_file)

    if not endpoints:
        print("❌ 未发现任何API端点")
        return

    # 生成catalog.yaml
    yaml_path = docs_dir / "catalog.yaml"
    generate_catalog_yaml(endpoints, yaml_path)

    # 生成catalog.md
    md_path = docs_dir / "catalog.md"
    generate_catalog_md(endpoints, md_path)

    # 打印统计
    p0_count = sum(1 for e in endpoints if e.priority == Priority.P0)
    p1_count = sum(1 for e in endpoints if e.priority == Priority.P1)
    p2_count = sum(1 for e in endpoints if e.priority == Priority.P2)

    print("\n📊 扫描统计:")
    print(f"  总计: {len(endpoints)} 个API")
    print(f"  P0: {p0_count} 个（核心业务）")
    print(f"  P1: {p1_count} 个（重要业务）")
    print(f"  P2: {p2_count} 个（辅助功能）")
    print(f"\n📁 输出文件:")
    print(f"  {yaml_path}")
    print(f"  {md_path}")


if __name__ == "__main__":
    main()
