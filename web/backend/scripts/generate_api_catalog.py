"""
API 目录生成器

从 FastAPI 应用生成完整的 API 目录文档，包括：
- 端点列表
- 请求/响应格式
- 契约状态
- 数据源状态
"""

import yaml
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class APICatalogGenerator:
    """API 目录生成器"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.catalog = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_endpoints": 0,
            "modules": {},
            "summary": {},
        }

    def generate_catalog(self) -> Dict[str, Any]:
        """生成完整 API 目录"""
        # 获取 OpenAPI schema
        openapi_schema = get_openapi(title=self.app.title, version=self.app.version, routes=self.app.routes)

        # 按路径分组
        paths = openapi_schema.get("paths", {})

        module_endpoints = {}
        method_counts = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}

        for path, methods in paths.items():
            # 从路径提取模块名
            parts = path.strip("/").split("/")
            module = parts[0] if parts else "root"
            if len(parts) > 1:
                module = f"{parts[0]}/{parts[1]}"

            if module not in module_endpoints:
                module_endpoints[module] = []

            for method, details in methods.items():
                if method.upper() not in method_counts:
                    continue
                method_counts[method.upper()] += 1

                endpoint_info = {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "tags": details.get("tags", []),
                    "parameters": self._extract_parameters(details),
                    "responses": self._extract_responses(details),
                    "deprecated": details.get("deprecated", False),
                }
                module_endpoints[module].append(endpoint_info)

        # 构建目录
        self.catalog["total_endpoints"] = sum(len(e) for e in module_endpoints.values())
        self.catalog["modules"] = module_endpoints
        self.catalog["summary"] = {
            "total_modules": len(module_endpoints),
            "total_endpoints": self.catalog["total_endpoints"],
            "method_counts": method_counts,
        }

        return self.catalog

    def _extract_parameters(self, details: Dict) -> List[Dict]:
        """提取参数信息"""
        params = []
        for param in details.get("parameters", []):
            params.append(
                {
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": param.get("required", False),
                    "schema": str(param.get("schema", {})),
                }
            )
        return params

    def _extract_responses(self, details: Dict) -> Dict:
        """提取响应信息"""
        responses = {}
        for code, response in details.get("responses", {}).items():
            responses[code] = {
                "description": response.get("description", ""),
                "has_schema": "content" in response and "application/json" in response.get("content", {}),
            }
        return responses

    def save_catalog(self, path: str = "docs/api/catalog.yaml"):
        """保存目录到文件"""
        import os

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.catalog, f, allow_unicode=True, sort_keys=False)

        print(f"✅ API Catalog saved to {path}")
        return self.catalog


def generate_api_markdown(catalog: Dict[str, Any]) -> str:
    """生成 Markdown 格式的 API 目录"""
    md = f"""# MyStocks API 目录

> 生成时间: {catalog["generated_at"]}

## 📊 统计摘要

| 指标 | 数值 |
|------|------|
| 总模块数 | {catalog["summary"]["total_modules"]} |
| 总端点数 | {catalog["summary"]["total_endpoints"]} |
| GET | {catalog["summary"]["method_counts"]["GET"]} |
| POST | {catalog["summary"]["method_counts"]["POST"]} |
| PUT | {catalog["summary"]["method_counts"]["PUT"]} |
| DELETE | {catalog["summary"]["method_counts"]["DELETE"]} |
| PATCH | {catalog["summary"]["method_counts"]["PATCH"]} |

---

## 📁 模块列表

"""

    for module, endpoints in catalog["modules"].items():
        md += f"### {module}\n\n"
        md += "| 方法 | 路径 | 描述 |\n"
        md += "|------|------|------|\n"

        for ep in endpoints:
            icon = "⚠️" if ep["deprecated"] else ""
            md += f"| **{ep['method']}** | `{ep['path']}` | {ep['summary']} {icon} |\n"

        md += "\n"

    return md


if __name__ == "__main__":
    from app.main import app

    generator = APICatalogGenerator(app)
    catalog = generator.generate_catalog()

    # 保存 YAML
    generator.save_catalog("docs/api/catalog.yaml")

    # 生成 Markdown
    md_content = generate_api_markdown(catalog)
    with open("docs/api/catalog.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("✅ API Catalog generated: docs/api/catalog.md")
