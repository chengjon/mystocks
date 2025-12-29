"""
契约验证服务
验证OpenAPI规范的正确性和完整性
"""

from typing import List, Dict, Any
import json

try:
    from prance import BaseParser

    PRANCE_AVAILABLE = True
except ImportError:
    PRANCE_AVAILABLE = False


from web.backend.app.api.contract.schemas import (
    ValidationResult,
    ContractValidateResponse,
)


class ContractValidator:
    """契约验证器"""

    @staticmethod
    def validate(
        spec: Dict[str, Any], check_breaking_changes: bool = True, compare_to_spec: Dict[str, Any] = None
    ) -> ContractValidateResponse:
        """
        验证OpenAPI规范

        Args:
            spec: 待验证的OpenAPI规范
            check_breaking_changes: 是否检查破坏性变更
            compare_to_spec: 对比的规范（用于破坏性变更检测）

        Returns:
            验证响应
        """
        results = []
        error_count = 0
        warning_count = 0

        # 1. 基础结构验证
        basic_errors = ContractValidator._validate_basic_structure(spec)
        results.extend(basic_errors)
        error_count += sum(1 for e in basic_errors if e.category == "error")
        warning_count += sum(1 for e in basic_errors if e.category == "warning")

        # 2. OpenAPI规范验证（如果prance可用）
        if PRANCE_AVAILABLE:
            openapi_errors = ContractValidator._validate_openapi_spec(spec)
            results.extend(openapi_errors)
            error_count += sum(1 for e in openapi_errors if e.category == "error")
            warning_count += sum(1 for e in openapi_errors if e.category == "warning")

        # 3. 破坏性变更检测
        if check_breaking_changes and compare_to_spec:
            breaking_errors = ContractValidator._check_breaking_changes(spec, compare_to_spec)
            results.extend(breaking_errors)
            warning_count += sum(1 for e in breaking_errors if e.category == "warning")

        # 4. 最佳实践检查
        practice_warnings = ContractValidator._check_best_practices(spec)
        results.extend(practice_warnings)
        warning_count += len(practice_warnings)

        valid = error_count == 0

        return ContractValidateResponse(
            valid=valid,
            error_count=error_count,
            warning_count=warning_count,
            results=results,
        )

    @staticmethod
    def _validate_basic_structure(spec: Dict[str, Any]) -> List[ValidationResult]:
        """
        验证基础结构

        Args:
            spec: OpenAPI规范

        Returns:
            验证结果列表
        """
        results = []

        # 检查必需字段
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in spec:
                results.append(
                    ValidationResult(
                        valid=False,
                        category="error",
                        path=f"/{field}",
                        message=f"缺少必需字段: {field}",
                        suggestion=f"添加 {field} 字段到OpenAPI规范根级别",
                    )
                )

        # 检查openapi版本
        if "openapi" in spec:
            openapi_version = str(spec["openapi"])
            if not openapi_version.startswith("3."):
                results.append(
                    ValidationResult(
                        valid=False,
                        category="warning",
                        path="/openapi",
                        message=f"不支持的OpenAPI版本: {openapi_version}",
                        suggestion="建议使用OpenAPI 3.0.x版本",
                    )
                )

        # 检查info
        if "info" in spec:
            info = spec["info"]
            info_required = ["title", "version"]
            for field in info_required:
                if field not in info:
                    results.append(
                        ValidationResult(
                            valid=False,
                            category="error",
                            path="/info",
                            message=f"info缺少必需字段: {field}",
                            suggestion=f"添加 {field} 字段到info对象",
                        )
                    )

        return results

    @staticmethod
    def _validate_openapi_spec(spec: Dict[str, Any]) -> List[ValidationResult]:
        """
        使用prance验证OpenAPI规范

        Args:
            spec: OpenAPI规范

        Returns:
            验证结果列表
        """
        results = []

        try:
            # 将spec写入临时文件
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                json.dump(spec, f)
                temp_path = f.name

            try:
                parser = BaseParser(temp_path, backend="openapi-spec")
                parser.parse()
                errors = parser.specification.get("errors", [])

                for error in errors:
                    results.append(
                        ValidationResult(
                            valid=False,
                            category="error",
                            path=error.get("path", "/"),
                            message=error.get("message", "OpenAPI规范错误"),
                            suggestion=error.get("suggestion"),
                        )
                    )

            finally:
                os.unlink(temp_path)

        except Exception as e:
            results.append(
                ValidationResult(
                    valid=False,
                    category="error",
                    path="/",
                    message=f"OpenAPI规范解析失败: {str(e)}",
                    suggestion="检查OpenAPI规范格式是否正确",
                )
            )

        return results

    @staticmethod
    def _check_breaking_changes(new_spec: Dict[str, Any], old_spec: Dict[str, Any]) -> List[ValidationResult]:
        """
        检查破坏性变更

        Args:
            new_spec: 新规范
            old_spec: 旧规范

        Returns:
            验证结果列表
        """
        results = []

        # 检查删除的API端点
        new_paths = set(new_spec.get("paths", {}).keys())
        old_paths = set(old_spec.get("paths", {}).keys())

        removed_paths = old_paths - new_paths
        for path in removed_paths:
            results.append(
                ValidationResult(
                    valid=False,
                    category="warning",
                    path=f"paths.{path}",
                    message=f"删除API端点: {path}",
                    suggestion="考虑保留旧端点或使用API版本控制",
                )
            )

        # 检查删除的Schema
        new_schemas = set(new_spec.get("components", {}).get("schemas", {}).keys())
        old_schemas = set(old_spec.get("components", {}).get("schemas", {}).keys())

        removed_schemas = old_schemas - new_schemas
        for schema in removed_schemas:
            results.append(
                ValidationResult(
                    valid=False,
                    category="warning",
                    path=f"components.schemas.{schema}",
                    message=f"删除Schema: {schema}",
                    suggestion="考虑标记为deprecated而非直接删除",
                )
            )

        return results

    @staticmethod
    def _check_best_practices(spec: Dict[str, Any]) -> List[ValidationResult]:
        """
        检查最佳实践

        Args:
            spec: OpenAPI规范

        Returns:
            验证结果列表
        """
        results = []

        # 检查API描述
        if "description" not in spec.get("info", {}):
            results.append(
                ValidationResult(
                    valid=True,
                    category="info",
                    path="/info/description",
                    message="缺少API描述",
                    suggestion="添加info.description字段以改善文档可读性",
                )
            )

        # 检查服务器配置
        servers = spec.get("servers", [])
        if not servers:
            results.append(
                ValidationResult(
                    valid=True,
                    category="info",
                    path="/servers",
                    message="缺少服务器配置",
                    suggestion="添加servers字段定义API服务器地址",
                )
            )

        # 检查操作ID
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if "operationId" not in details:
                    results.append(
                        ValidationResult(
                            valid=True,
                            category="info",
                            path=f"paths.{path}.{method}",
                            message=f"缺少operationId: {method} {path}",
                            suggestion="添加operationId字段以便于生成客户端SDK",
                        )
                    )

        return results
