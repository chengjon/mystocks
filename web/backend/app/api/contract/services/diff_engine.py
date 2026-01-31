"""
契约差异检测引擎
使用语义化对比检测OpenAPI规范的差异
"""

from typing import Any, Dict, List, Optional

try:
    from deepdiff import DeepDiff

    DEEPDIFF_AVAILABLE = True
except ImportError:
    DEEPDIFF_AVAILABLE = False


from app.api.contract.schemas import (
    ContractDiffResponse,
    DiffResult,
)


class DiffEngine:
    """契约差异检测引擎"""

    # 破坏性变更规则
    BREAKING_CHANGES = {
        # 删除操作
        "paths.* removed": "删除API端点",
        "paths.*.*.delete removed": "删除DELETE方法",
        "paths.*.*.get removed": "删除GET方法",
        "paths.*.*.post removed": "删除POST方法",
        "paths.*.*.put removed": "删除PUT方法",
        "paths.*.*.patch removed": "删除PATCH方法",
        # 删除必需参数
        "paths.*.*.*.parameters.* removed": "删除路径参数或查询参数",
        "components.schemas.*.required.* removed": "删除必需字段",
        # 修改参数类型
        "paths.*.*.*.parameters.*.schema.type changed": "修改参数类型",
        "paths.*.*.*.requestBody.content.*.schema.type changed": "修改请求体类型",
        # 删除响应状态码
        "paths.*.*.*.responses.* removed": "删除响应状态码",
        # 删除Schema
        "components.schemas.* removed": "删除Schema定义",
        "components.schemas.*.properties.* removed": "删除Schema属性",
        "components.schemas.*.required changed": "修改必需字段列表",
    }

    @staticmethod
    def compare_versions(
        from_spec: Dict[str, Any], to_spec: Dict[str, Any], from_version: str, to_version: str
    ) -> ContractDiffResponse:
        """
        对比两个契约版本

        Args:
            from_spec: 源版本OpenAPI规范
            to_spec: 目标版本OpenAPI规范
            from_version: 源版本号
            to_version: 目标版本号

        Returns:
            契约差异响应
        """
        if not DEEPDIFF_AVAILABLE:
            return DiffEngine._simple_diff(from_spec, to_spec, from_version, to_version)

        # 使用DeepDiff进行深度对比
        diff = DeepDiff(
            from_spec,
            to_spec,
            ignore_order=True,
            report_type="tree",
        )

        # 解析差异
        diffs = []
        breaking_count = 0
        non_breaking_count = 0

        for change_type, changes in diff.to_dict().items():
            if not changes:
                continue

            for change in changes:
                diff_result = DiffEngine._parse_change(change_type, change)
                if diff_result:
                    # 判断是否为破坏性变更
                    diff_result.is_breaking = DiffEngine._is_breaking_change(diff_result.path, diff_result.change_type)

                    if diff_result.is_breaking:
                        breaking_count += 1
                    else:
                        non_breaking_count += 1

                    diffs.append(diff_result)

        # 生成摘要
        summary = DiffEngine._generate_summary(diffs, breaking_count, non_breaking_count)

        return ContractDiffResponse(
            from_version=from_version,
            to_version=to_version,
            total_changes=len(diffs),
            breaking_changes=breaking_count,
            non_breaking_changes=non_breaking_count,
            diffs=diffs,
            summary=summary,
        )

    @staticmethod
    def _parse_change(change_type: str, change: Any) -> Optional[DiffResult]:
        """
        解析单个变更

        Args:
            change_type: 变更类型
            change: 变更详情

        Returns:
            差异结果
        """
        if not DEEPDIFF_AVAILABLE:
            return None

        try:
            # 获取路径
            if hasattr(change, "path"):
                path = change.path(output_format="string")
            else:
                return None

            # 获取值
            old_value = None
            new_value = None

            if change_type == "values_changed":
                old_value = change.t1
                new_value = change.t2
            elif change_type == "dictionary_item_added":
                new_value = change.t2
            elif change_type == "dictionary_item_removed":
                old_value = change.t1
            elif change_type == "iterable_item_added":
                new_value = change.t2
            elif change_type == "iterable_item_removed":
                old_value = change.t1

            return DiffResult(
                change_type=change_type,
                path=path,
                old_value=old_value,
                new_value=new_value,
            )

        except Exception:
            return None

    @staticmethod
    def _is_breaking_change(path: str, change_type: str) -> bool:
        """
        判断是否为破坏性变更

        Args:
            path: 变更路径
            change_type: 变更类型

        Returns:
            是否为破坏性变更
        """
        # 删除操作通常是破坏性的
        if "removed" in change_type:
            return True

        # 检查是否匹配破坏性变更规则
        for pattern in DiffEngine.BREAKING_CHANGES:
            # 简单的通配符匹配
            pattern_parts = pattern.split(".")
            path_parts = path.split(".")

            if DiffEngine._match_pattern(pattern_parts, path_parts):
                return True

        return False

    @staticmethod
    def _match_pattern(pattern: List[str], path: List[str]) -> bool:
        """
        匹配路径模式

        Args:
            pattern: 模式列表
            path: 路径列表

        Returns:
            是否匹配
        """
        for i, part in enumerate(pattern):
            if part == "*":
                continue
            if i >= len(path):
                return False
            if part != path[i]:
                return False

        return True

    @staticmethod
    def _generate_summary(diffs: List[DiffResult], breaking_count: int, non_breaking_count: int) -> str:
        """
        生成差异摘要

        Args:
            diffs: 差异列表
            breaking_count: 破坏性变更数
            non_breaking_count: 非破坏性变更数

        Returns:
            摘要文本
        """
        lines = [
            f"总变更数: {len(diffs)}",
            f"破坏性变更: {breaking_count}",
            f"非破坏性变更: {non_breaking_count}",
        ]

        if breaking_count > 0:
            lines.append("")
            lines.append("⚠️ 警告: 检测到破坏性变更，请谨慎评估！")

            # 列出主要破坏性变更
            breaking = [d for d in diffs if d.is_breaking][:5]
            for diff in breaking:
                lines.append(f"  - {diff.path}")

        return "\n".join(lines)

    @staticmethod
    def _simple_diff(
        from_spec: Dict[str, Any], to_spec: Dict[str, Any], from_version: str, to_version: str
    ) -> ContractDiffResponse:
        """
        简单差异对比（当deepdiff不可用时）

        Args:
            from_spec: 源版本OpenAPI规范
            to_spec: 目标版本OpenAPI规范
            from_version: 源版本号
            to_version: 目标版本号

        Returns:
            契约差异响应
        """
        diffs = []

        # 对比paths
        from_paths = from_spec.get("paths", {})
        to_paths = to_spec.get("paths", {})

        all_paths = set(from_paths.keys()) | set(to_paths.keys())

        for path in all_paths:
            if path not in from_paths:
                diffs.append(
                    DiffResult(
                        change_type="added",
                        path=f"paths.{path}",
                        new_value=to_paths[path],
                        is_breaking=False,
                        description=f"新增API端点: {path}",
                    )
                )
            elif path not in to_paths:
                diffs.append(
                    DiffResult(
                        change_type="removed",
                        path=f"paths.{path}",
                        old_value=from_paths[path],
                        is_breaking=True,
                        description=f"删除API端点: {path}",
                    )
                )

        # 对比schemas
        from_schemas = from_spec.get("components", {}).get("schemas", {})
        to_schemas = to_spec.get("components", {}).get("schemas", {})

        all_schemas = set(from_schemas.keys()) | set(to_schemas.keys())

        for schema in all_schemas:
            if schema not in from_schemas:
                diffs.append(
                    DiffResult(
                        change_type="added",
                        path=f"components.schemas.{schema}",
                        new_value=to_schemas[schema],
                        is_breaking=False,
                        description=f"新增Schema: {schema}",
                    )
                )
            elif schema not in to_schemas:
                diffs.append(
                    DiffResult(
                        change_type="removed",
                        path=f"components.schemas.{schema}",
                        old_value=from_schemas[schema],
                        is_breaking=True,
                        description=f"删除Schema: {schema}",
                    )
                )

        breaking_count = sum(1 for d in diffs if d.is_breaking)
        non_breaking_count = len(diffs) - breaking_count

        summary = DiffEngine._generate_summary(diffs, breaking_count, non_breaking_count)

        return ContractDiffResponse(
            from_version=from_version,
            to_version=to_version,
            total_changes=len(diffs),
            breaking_changes=breaking_count,
            non_breaking_changes=non_breaking_count,
            diffs=diffs,
            summary=summary,
        )
