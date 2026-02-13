"""
API 契约注册中心

自动注册所有 API 端点到契约管理系统。
确保每个端点都有对应的契约定义。
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EndpointContract:
    """端点契约信息"""

    module: str
    path: str
    method: str
    operation_id: str
    summary: str
    description: str
    tags: List[str]
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None
    registered: bool = False
    contract_version: Optional[str] = None


class ContractRegistry:
    """契约注册中心"""

    def __init__(self):
        self.contracts: Dict[str, EndpointContract] = {}
        self.modules: Dict[str, Dict] = {}

    def register_from_openapi(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        从 OpenAPI spec 注册所有端点契约

        Returns:
            注册报告
        """
        registered = 0
        skipped = 0
        errors = []

        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    continue

                operation_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
                key = f"{method.upper()} {path}"

                try:
                    contract = EndpointContract(
                        module=self._extract_module(path),
                        path=path,
                        method=method.upper(),
                        operation_id=operation_id,
                        summary=details.get("summary", ""),
                        description=details.get("description", ""),
                        tags=details.get("tags", []),
                        request_schema=self._extract_request_schema(details),
                        response_schema=self._extract_response_schema(details),
                    )

                    self.contracts[key] = contract
                    registered += 1

                except Exception as e:
                    errors.append({"endpoint": f"{method} {path}", "error": str(e)})
                    skipped += 1

        # 更新模块统计
        self._update_module_stats()

        return {
            "registered": registered,
            "skipped": skipped,
            "errors": errors,
            "total": len(self.contracts),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_module(self, path: str) -> str:
        """从路径提取模块名"""
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return parts[0] if parts else "root"

    def _extract_request_schema(self, details: Dict) -> Optional[Dict]:
        """提取请求 schema"""
        request_body = details.get("requestBody", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        return json_content.get("schema")

    def _extract_response_schema(self, details: Dict) -> Optional[Dict]:
        """提取响应 schema"""
        responses = details.get("responses", {})
        success_response = responses.get("200", responses.get("201", {}))
        content = success_response.get("content", {})
        json_content = content.get("application/json", {})
        return json_content.get("schema")

    def _update_module_stats(self):
        """更新模块统计"""
        for key, contract in self.contracts.items():
            module = contract.module
            if module not in self.modules:
                self.modules[module] = {"name": module, "endpoints": [], "total": 0, "registered": 0}
            self.modules[module]["endpoints"].append(
                {"path": contract.path, "method": contract.method, "operation_id": contract.operation_id}
            )
            self.modules[module]["total"] += 1

    def get_unregistered_endpoints(self) -> List[Dict]:
        """获取未注册到契约管理的端点"""
        unregistered = []
        for key, contract in self.contracts.items():
            if not contract.registered:
                unregistered.append(
                    {
                        "module": contract.module,
                        "path": contract.path,
                        "method": contract.method,
                        "operation_id": contract.operation_id,
                    }
                )
        return unregistered

    def export_registry(self) -> Dict[str, Any]:
        """导出注册表"""
        return {
            "total_contracts": len(self.contracts),
            "total_modules": len(self.modules),
            "modules": self.modules,
            "unregistered_count": len(self.get_unregistered_endpoints()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# 全局注册表实例
contract_registry = ContractRegistry()
