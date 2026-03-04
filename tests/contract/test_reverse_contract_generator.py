"""
反向工程契约生成器

从运行中的服务自动生成API契约，支持Swagger/OpenAPI文档和HTTP接口扫描。
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx


class ScannerType(Enum):
    """扫描器类型枚举"""

    AUTO_DETECT = "auto_detect"
    SWAGGER_UI = "swagger_ui"
    OPENAPI_JSON = "openapi_json"
    OPENAPI_YAML = "openapi_yaml"
    MANUAL_SCAN = "manual_scan"
    REVERSE_ENGINEER = "reverse_engineer"


@dataclass
class Endpoint:
    """端点定义"""

    path: str
    method: str
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Dict[str, Any] = field(default_factory=dict)
    responses: List[Dict[str, Any]] = field(default_factory=list)
    security: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    """扫描结果"""

    scanner_type: ScannerType
    base_url: str
    endpoints: List[Endpoint]
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    scan_duration: float = 0.0
    errors: List[str] = field(default_factory=list)


class WebScraper:
    """网页爬取器"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = httpx.AsyncClient(timeout=timeout, verify=False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    async def fetch_page(self, url: str) -> str:
        """获取网页内容"""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            raise Exception(f"获取网页失败: {e}")

    async def fetch_json(self, url: str) -> Dict[str, Any]:
        """获取JSON数据"""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"获取JSON数据失败: {e}")

    async def discover_endpoints(self, base_url: str) -> List[str]:
        """发现端点"""
        discovered = []

        # 常见端点发现
        common_paths = [
            "/api",
            "/v1/api",
            "/v2/api",
            "/rest",
            "/swagger.json",
            "/swagger.yaml",
            "/openapi.json",
            "/openapi.yaml",
            "/docs",
            "/redoc",
            "/api-docs",
            "/api/v1",
            "/api/v2",
        ]

        for path in common_paths:
            url = urljoin(base_url, path)
            try:
                response = await self.session.get(url, follow_redirects=True)
                if response.status_code < 400:
                    discovered.append(path)
                    print(f"  ✓ 发现端点: {path}")
                else:
                    print(f"  ✗ 端点不可用: {path} (HTTP {response.status_code})")
            except Exception as e:
                print(f"  ✗ 端点访问失败: {path} - {e}")

        return discovered


class SwaggerUIParser:
    """Swagger UI解析器"""

    def __init__(self):
        self.patterns = {
            "swagger_json": re.compile(
                r'window\.__REDUX_STATE__\s*=\s*({[^}]*"swagger":\s*{[^}]*}[^}]*})',
                re.DOTALL,
            ),
            "openapi_json": re.compile(
                r'window\.__INITIAL_REDUX_STATE__\s*=\s*({[^}]*"openapi":\s*{[^}]*}[^}]*})',
                re.DOTALL,
            ),
            "spec_url": re.compile(r'url:\s*["\']([^"\']+)["\'],\s*spec:', re.DOTALL),
        }

    async def parse(self, base_url: str) -> Dict[str, Any]:
        """解析Swagger UI"""
        # 获取文档页面
        web_scraper = WebScraper()
        async with web_scraper:
            content = await web_scraper.fetch_page(base_url)

            # 尝试从页面提取JSON
            swagger_json_match = self.patterns["swagger_json"].search(content)
            if swagger_json_match:
                try:
                    return json.loads(swagger_json_match.group(1))
                except json.JSONDecodeError:
                    pass

            openapi_json_match = self.patterns["openapi_json"].search(content)
            if openapi_json_match:
                try:
                    return json.loads(openapi_json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # 尝试直接访问openapi.json
            try:
                openapi_url = urljoin(base_url, "/openapi.json")
                return await web_scraper.fetch_json(openapi_url)
            except Exception:
                pass

            # 尝试直接访问swagger.json
            try:
                swagger_url = urljoin(base_url, "/swagger.json")
                return await web_scraper.fetch_json(swagger_url)
            except Exception:
                pass

            raise Exception("无法从Swagger UI获取API规范")


class OpenAPIScraper:
    """OpenAPI爬取器"""

    async def scrape_from_url(self, url: str) -> Dict[str, Any]:
        """从URL爬取OpenAPI规范"""
        web_scraper = WebScraper()
        async with web_scraper:
            return await web_scraper.fetch_json(url)

    async def discover_openapi_docs(self, base_url: str) -> Optional[str]:
        """发现OpenAPI文档位置"""
        possible_paths = [
            "/openapi.json",
            "/swagger.json",
            "/api/openapi.json",
            "/api/swagger.json",
            "/v1/openapi.json",
            "/v2/openapi.json",
            "/docs/swagger.json",
            "/docs/openapi.json",
        ]

        web_scraper = WebScraper()
        async with web_scraper:
            for path in possible_paths:
                try:
                    full_url = urljoin(base_url, path)
                    response = await web_scraper.session.get(full_url)
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "").lower()
                        if "json" in content_type:
                            print(f"  ✓ 发现OpenAPI文档: {path}")
                            return full_url
                except Exception:
                    continue

        return None


class HTTPScanner:
    """HTTP扫描器"""

    def __init__(self, timeout: int = 10, max_concurrent: int = 10):
        self.timeout = timeout
        self.max_concurrent = max_concurrent

    async def scan_endpoints(self, base_url: str, paths: List[str]) -> List[Dict[str, Any]]:
        """扫描端点"""
        discovered_endpoints = []

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def scan_endpoint(path: str) -> Optional[Dict[str, Any]]:
            async with semaphore:
                url = urljoin(base_url, path)
                try:
                    # 尝试HTTP方法
                    methods = [
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "PATCH",
                        "HEAD",
                        "OPTIONS",
                    ]
                    for method in methods:
                        try:
                            response = await self._send_request(method, url)
                            if response.status_code < 500:
                                return {
                                    "path": path,
                                    "method": method,
                                    "status_code": response.status_code,
                                    "content_type": response.headers.get("content-type", ""),
                                    "content_length": response.headers.get("content-length", "0"),
                                }
                        except Exception:
                            continue
                    return None
                except Exception:
                    return None

        tasks = [scan_endpoint(path) for path in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, dict) and result:
                discovered_endpoints.append(result)

        return discovered_endpoints

    async def _send_request(self, method: str, url: str) -> httpx.Response:
        """发送HTTP请求"""
        client = httpx.AsyncClient(timeout=self.timeout, verify=False)
        try:
            response = await client.request(method, url)
            return response
        finally:
            await client.aclose()


class ReverseContractGenerator:
    """反向工程契约生成器"""

    def __init__(self, timeout: int = 30, max_concurrent: int = 10):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.web_scraper = WebScraper(timeout)
        self.swagger_parser = SwaggerUIParser()
        self.openapi_scraper = OpenAPIScraper()
        self.http_scanner = HTTPScanner(timeout, max_concurrent)

    async def generate_contract(self, url: str, scanner_type: ScannerType = ScannerType.AUTO_DETECT) -> ScanResult:
        """生成契约"""
        start_time = time.time()
        base_url = self._normalize_url(url)

        scan_result = ScanResult(scanner_type=scanner_type, base_url=base_url, endpoints=[])

        try:
            if scanner_type == ScannerType.SWAGGER_UI:
                await self._scan_from_swagger_ui(scan_result)
            elif scanner_type == ScannerType.OPENAPI_JSON:
                await self._scan_from_openapi_json(scan_result)
            elif scanner_type == ScannerType.MANUAL_SCAN:
                await self._manual_scan(scan_result)
            elif scanner_type == ScannerType.REVERSE_ENGINEER:
                await self._reverse_engineer(scan_result)
            else:
                # 自动检测
                await self._auto_scan(scan_result)

            scan_result.scan_duration = time.time() - start_time

            print("\n📊 扫描结果:")
            print(f"  扫描器: {scan_result.scanner_type.value}")
            print(f"  基础URL: {scan_result.base_url}")
            print(f"  端点数量: {len(scan_result.endpoints)}")
            print(f"  耗时: {scan_result.scan_duration:.2f}秒")

            return scan_result

        except Exception as e:
            scan_result.scan_duration = time.time() - start_time
            scan_result.errors.append(str(e))
            print(f"❌ 扫描失败: {e}")
            raise

    async def _auto_scan(self, scan_result: ScanResult):
        """自动扫描"""
        print("🔍 开始自动扫描...")

        # 首先尝试从Swagger UI解析
        try:
            spec = await self.swagger_parser.parse(scan_result.base_url)
            await self._parse_openapi_spec(spec, scan_result)
            scan_result.scanner_type = ScannerType.SWAGGER_UI
            return
        except Exception:
            pass

        # 尝试直接获取OpenAPI JSON
        try:
            openapi_url = await self.openapi_scraper.discover_openapi_docs(scan_result.base_url)
            if openapi_url:
                spec = await self.openapi_scraper.scrape_from_url(openapi_url)
                await self._parse_openapi_spec(spec, scan_result)
                scan_result.scanner_type = ScannerType.OPENAPI_JSON
                return
        except Exception:
            pass

        # 如果以上都失败，使用手动扫描
        await self._manual_scan(scan_result)
        scan_result.scanner_type = ScannerType.MANUAL_SCAN

    async def _scan_from_swagger_ui(self, scan_result: ScanResult):
        """从Swagger UI扫描"""
        print("📖 从Swagger UI解析...")
        spec = await self.swagger_parser.parse(scan_result.base_url)
        await self._parse_openapi_spec(spec, scan_result)

    async def _scan_from_openapi_json(self, scan_result: ScanResult):
        """从OpenAPI JSON扫描"""
        print("📄 从OpenAPI JSON解析...")
        spec = await self.openapi_scraper.scrape_from_url(scan_result.base_url)
        await self._parse_openapi_spec(spec, scan_result)

    async def _manual_scan(self, scan_result: ScanResult):
        """手动扫描"""
        print("🔧 开始手动扫描...")

        web_scraper = WebScraper()
        async with web_scraper:
            # 发现端点
            discovered_paths = await web_scraper.discover_endpoints(scan_result.base_url)
            print(f"  发现 {len(discovered_paths)} 个可能的端点")

            # 扫描端点
            discovered_endpoints = await self.http_scanner.scan_endpoints(scan_result.base_url, discovered_paths)

            # 转换为端点对象
            for endpoint_info in discovered_endpoints:
                endpoint = Endpoint(
                    path=endpoint_info["path"],
                    method=endpoint_info["method"],
                    responses=[
                        {
                            "status_code": endpoint_info["status_code"],
                            "description": "Successful response",
                        }
                    ],
                )
                scan_result.endpoints.append(endpoint)

    async def _reverse_engineer(self, scan_result: ScanResult):
        """反向工程扫描"""
        print("⚙️ 开始反向工程扫描...")

        # 这里可以实现更复杂的反向工程逻辑
        # 例如通过分析网页内容来推断API端点
        await self._manual_scan(scan_result)

    async def _parse_openapi_spec(self, spec: Dict[str, Any], scan_result: ScanResult):
        """解析OpenAPI规范"""
        if not spec or "paths" not in spec:
            raise Exception("无效的OpenAPI规范")

        paths = spec["paths"]
        metadata = spec.get("info", {})
        scan_result.metadata = metadata

        for path, path_data in paths.items():
            for method, method_data in path_data.items():
                if method.upper() not in [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                ]:
                    continue

                # 创建端点
                endpoint = Endpoint(
                    path=path,
                    method=method.upper(),
                    summary=method_data.get("summary", ""),
                    description=method_data.get("description", ""),
                    tags=method_data.get("tags", []),
                    deprecated=method_data.get("deprecated", False),
                )

                # 解析参数
                if "parameters" in method_data:
                    for param in method_data["parameters"]:
                        endpoint.parameters.append(param)

                # 解析请求体
                if "requestBody" in method_data:
                    endpoint.request_body = method_data["requestBody"]

                # 解析响应
                if "responses" in method_data:
                    for status_code, response_data in method_data["responses"].items():
                        endpoint.responses.append(
                            {
                                "status_code": int(status_code),
                                "description": response_data.get("description", ""),
                                "content": response_data.get("content", {}),
                            }
                        )

                # 解析安全要求
                if "security" in method_data:
                    endpoint.security = method_data["security"]

                scan_result.endpoints.append(endpoint)

    def _normalize_url(self, url: str) -> str:
        """标准化URL"""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def export_contract(
        self,
        scan_result: ScanResult,
        format: str = "openapi",
        output_path: Optional[str] = None,
    ):
        """导出契约"""
        if format.lower() == "openapi":
            contract = self._convert_to_openapi(scan_result)
        elif format.lower() == "swagger":
            contract = self._convert_to_swagger(scan_result)
        else:
            raise ValueError(f"不支持的格式: {format}")

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                if format.lower() in ["openapi", "swagger"]:
                    json.dump(contract, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"不支持导出格式: {format}")

        print(f"✓ 契约已导出: {output_path}")
        return contract

    def _convert_to_openapi(self, scan_result: ScanResult) -> Dict[str, Any]:
        """转换为OpenAPI格式"""
        contract = {
            "openapi": "3.0.0",
            "info": scan_result.metadata,
            "servers": [
                {
                    "url": scan_result.base_url,
                    "description": "Generated from reverse engineering",
                }
            ],
            "paths": {},
        }

        for endpoint in scan_result.endpoints:
            if endpoint.path not in contract["paths"]:
                contract["paths"][endpoint.path] = {}

            method_spec = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "deprecated": endpoint.deprecated,
            }

            # 添加参数
            if endpoint.parameters:
                method_spec["parameters"] = endpoint.parameters

            # 添加请求体
            if endpoint.request_body:
                method_spec["requestBody"] = endpoint.request_body

            # 添加响应
            if endpoint.responses:
                method_spec["responses"] = {}
                for response in endpoint.responses:
                    method_spec["responses"][str(response["status_code"])] = {
                        "description": response["description"],
                        "content": response.get("content", {}),
                    }

            # 添加安全要求
            if endpoint.security:
                method_spec["security"] = endpoint.security

            contract["paths"][endpoint.path][endpoint.method.lower()] = method_spec

        return contract

    def _convert_to_swagger(self, scan_result: ScanResult) -> Dict[str, Any]:
        """转换为Swagger 2.0格式"""
        contract = self._convert_to_openapi(scan_result)
        # 这里可以添加Swagger特定的转换逻辑
        return contract

    def analyze_api_coverage(self, scan_result: ScanResult) -> Dict[str, Any]:
        """分析API覆盖率"""
        coverage = {
            "total_endpoints": len(scan_result.endpoints),
            "by_method": {},
            "by_status_code": {},
            "by_path_pattern": {},
            "security_endpoints": 0,
            "deprecated_endpoints": 0,
        }

        for endpoint in scan_result.endpoints:
            # 按方法统计
            method = endpoint.method
            coverage["by_method"][method] = coverage["by_method"].get(method, 0) + 1

            # 按状态码统计
            if endpoint.responses:
                for response in endpoint.responses:
                    status = response["status_code"]
                    coverage["by_status_code"][status] = coverage["by_status_code"].get(status, 0) + 1

            # 按路径模式统计
            path_pattern = self._extract_path_pattern(endpoint.path)
            coverage["by_path_pattern"][path_pattern] = coverage["by_path_pattern"].get(path_pattern, 0) + 1

            # 安全端点
            if endpoint.security:
                coverage["security_endpoints"] += 1

            # 已废弃端点
            if endpoint.deprecated:
                coverage["deprecated_endpoints"] += 1

        return coverage

    def _extract_path_pattern(self, path: str) -> str:
        """提取路径模式"""
        # 将路径参数替换为占位符
        pattern = re.sub(r"\{[^}]+\}", "{param}", path)
        return pattern


# 使用示例
async def demo_reverse_contract_generator():
    """演示反向工程契约生成器"""
    print("🚀 演示反向工程契约生成器")

    # 创建生成器
    generator = ReverseContractGenerator(timeout=15, max_concurrent=5)

    # 演示URL（替换为实际的目标API）
    test_urls = [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com",
        "http://localhost:8020",  # 如果本地有运行的服务
    ]

    for url in test_urls:
        print(f"\n🔗 测试URL: {url}")
        try:
            # 生成契约
            scan_result = await generator.generate_contract(url, ScannerType.AUTO_DETECT)

            # 分析覆盖率
            coverage = generator.analyze_api_coverage(scan_result)
            print("\n📊 API覆盖率分析:")
            print(f"  总端点数: {coverage['total_endpoints']}")
            print(f"  按方法分布: {coverage['by_method']}")
            print(f"  安全端点: {coverage['security_endpoints']}")
            print(f"  已废弃端点: {coverage['deprecated_endpoints']}")

            # 导出契约
            contract = generator.export_contract(
                scan_result,
                format="openapi",
                output_path=f"reverse_contract_{url.replace('://', '_')}.json",
            )

            print("✅ 反向工程演示完成")
            break

        except Exception as e:
            print(f"❌ 演示失败: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(demo_reverse_contract_generator())
