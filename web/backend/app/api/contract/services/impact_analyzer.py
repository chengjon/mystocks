"""Contract impact analysis service.

This module is intentionally side-effect free: it does not touch the database,
routes, or application state. API endpoints can compose it later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ContractImpactItem:
    """Single contract change impact."""

    category: str
    name: str
    path: str
    change_type: str
    severity: str
    is_breaking: bool
    reason: str


@dataclass(frozen=True)
class ContractImpactSummary:
    """Aggregated impact counts."""

    total_impacts: int
    breaking_impacts: int
    non_breaking_impacts: int
    by_category: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ContractImpactAnalysis:
    """Contract impact analysis result."""

    from_version: str
    to_version: str
    risk_level: str
    summary: ContractImpactSummary
    impacts: list[ContractImpactItem]
    affected_endpoints: list[str]
    affected_schemas: list[str]
    affected_clients: list[str]
    recommendations: list[str]


class ContractImpactAnalyzer:
    """Analyze consumer-facing impact between two OpenAPI contract specs."""

    def analyze_specs(
        self,
        from_spec: Mapping[str, Any],
        to_spec: Mapping[str, Any],
        from_version: str = "unknown",
        to_version: str = "unknown",
    ) -> ContractImpactAnalysis:
        """Analyze endpoint and schema impact between two OpenAPI specs."""

        impacts = [
            *self._analyze_endpoint_impacts(from_spec, to_spec),
            *self._analyze_schema_impacts(from_spec, to_spec),
        ]
        return self._build_analysis(from_version, to_version, impacts)

    def analyze_diff(
        self,
        diffs: Iterable[Any],
        from_version: str = "unknown",
        to_version: str = "unknown",
    ) -> ContractImpactAnalysis:
        """Analyze impact from existing diff result objects or dictionaries."""

        impacts = [impact for diff in diffs for impact in self._impact_from_diff(diff)]
        return self._build_analysis(from_version, to_version, impacts)

    def _analyze_endpoint_impacts(
        self,
        from_spec: Mapping[str, Any],
        to_spec: Mapping[str, Any],
    ) -> list[ContractImpactItem]:
        from_endpoints = self._extract_endpoints(from_spec)
        to_endpoints = self._extract_endpoints(to_spec)
        impacts: list[ContractImpactItem] = []

        for endpoint_key, endpoint in sorted(from_endpoints.items()):
            if endpoint_key not in to_endpoints:
                impacts.append(
                    ContractImpactItem(
                        category="endpoint",
                        name=endpoint_key,
                        path=endpoint["path"],
                        change_type="removed",
                        severity="critical",
                        is_breaking=True,
                        reason=f"Endpoint {endpoint_key} was removed",
                    )
                )

        for endpoint_key, endpoint in sorted(to_endpoints.items()):
            if endpoint_key not in from_endpoints:
                impacts.append(
                    ContractImpactItem(
                        category="endpoint",
                        name=endpoint_key,
                        path=endpoint["path"],
                        change_type="added",
                        severity="medium",
                        is_breaking=False,
                        reason=f"Endpoint {endpoint_key} was added",
                    )
                )

        return impacts

    def _analyze_schema_impacts(
        self,
        from_spec: Mapping[str, Any],
        to_spec: Mapping[str, Any],
    ) -> list[ContractImpactItem]:
        from_schemas = self._extract_schemas(from_spec)
        to_schemas = self._extract_schemas(to_spec)
        impacts: list[ContractImpactItem] = []

        for schema_name, schema in sorted(from_schemas.items()):
            if schema_name not in to_schemas:
                impacts.append(
                    ContractImpactItem(
                        category="schema",
                        name=schema_name,
                        path=f"components.schemas.{schema_name}",
                        change_type="removed",
                        severity="high",
                        is_breaking=True,
                        reason=f"Schema {schema_name} was removed",
                    )
                )
                continue

            impacts.extend(self._analyze_schema_property_impacts(schema_name, schema, to_schemas[schema_name]))

        for schema_name in sorted(set(to_schemas) - set(from_schemas)):
            impacts.append(
                ContractImpactItem(
                    category="schema",
                    name=schema_name,
                    path=f"components.schemas.{schema_name}",
                    change_type="added",
                    severity="low",
                    is_breaking=False,
                    reason=f"Schema {schema_name} was added",
                )
            )

        return impacts

    def _analyze_schema_property_impacts(
        self,
        schema_name: str,
        from_schema: Mapping[str, Any],
        to_schema: Mapping[str, Any],
    ) -> list[ContractImpactItem]:
        from_properties = self._as_mapping(from_schema.get("properties"))
        to_properties = self._as_mapping(to_schema.get("properties"))
        from_required = set(self._as_list(from_schema.get("required")))
        to_required = set(self._as_list(to_schema.get("required")))
        impacts: list[ContractImpactItem] = []

        for property_name in sorted(set(from_properties) - set(to_properties)):
            impacts.append(
                ContractImpactItem(
                    category="schema",
                    name=f"{schema_name}.{property_name}",
                    path=f"components.schemas.{schema_name}.properties.{property_name}",
                    change_type="removed",
                    severity="high",
                    is_breaking=True,
                    reason=f"Schema property {schema_name}.{property_name} was removed",
                )
            )

        for property_name in sorted(to_required - from_required):
            impacts.append(
                ContractImpactItem(
                    category="schema",
                    name=f"{schema_name}.{property_name}",
                    path=f"components.schemas.{schema_name}.required.{property_name}",
                    change_type="required_added",
                    severity="high",
                    is_breaking=True,
                    reason=f"Schema property {schema_name}.{property_name} became required",
                )
            )

        return impacts

    def _impact_from_diff(self, diff: Any) -> list[ContractImpactItem]:
        path = str(self._get_value(diff, "path", ""))
        change_type = str(self._get_value(diff, "change_type", "modified"))
        is_breaking = bool(self._get_value(diff, "is_breaking", False))

        if not path:
            return []

        category = self._category_from_path(path)
        name = self._name_from_path(category, path)
        severity = self._severity_for(category, change_type, is_breaking)

        return [
            ContractImpactItem(
                category=category,
                name=name,
                path=path,
                change_type=change_type,
                severity=severity,
                is_breaking=is_breaking,
                reason=f"{category} impact detected at {path}",
            )
        ]

    def _build_analysis(
        self,
        from_version: str,
        to_version: str,
        impacts: list[ContractImpactItem],
    ) -> ContractImpactAnalysis:
        by_category: dict[str, int] = {}
        for impact in impacts:
            by_category[impact.category] = by_category.get(impact.category, 0) + 1

        breaking_impacts = sum(1 for impact in impacts if impact.is_breaking)
        summary = ContractImpactSummary(
            total_impacts=len(impacts),
            breaking_impacts=breaking_impacts,
            non_breaking_impacts=len(impacts) - breaking_impacts,
            by_category=by_category,
        )

        return ContractImpactAnalysis(
            from_version=from_version,
            to_version=to_version,
            risk_level=self._risk_level(impacts),
            summary=summary,
            impacts=impacts,
            affected_endpoints=self._unique_sorted(impact.path for impact in impacts if impact.category == "endpoint"),
            affected_schemas=self._affected_schemas(impacts),
            affected_clients=self._affected_clients(impacts),
            recommendations=self._recommendations(impacts),
        )

    def _extract_endpoints(self, spec: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        endpoints: dict[str, dict[str, Any]] = {}
        paths = self._as_mapping(spec.get("paths"))
        for path, methods in paths.items():
            for method, details in self._as_mapping(methods).items():
                if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                    continue
                endpoint_key = f"{method.upper()} {path}"
                endpoint_details = self._as_mapping(details)
                endpoints[endpoint_key] = {
                    "path": path,
                    "method": method.upper(),
                    "tags": self._as_list(endpoint_details.get("tags")),
                }
        return endpoints

    def _extract_schemas(self, spec: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
        components = self._as_mapping(spec.get("components"))
        schemas = self._as_mapping(components.get("schemas"))
        return {str(name): self._as_mapping(schema) for name, schema in schemas.items()}

    def _affected_schemas(self, impacts: list[ContractImpactItem]) -> list[str]:
        schemas = []
        for impact in impacts:
            if impact.category != "schema":
                continue
            schemas.append(impact.name.split(".", 1)[0])
        return self._unique_sorted(schemas)

    def _affected_clients(self, impacts: list[ContractImpactItem]) -> list[str]:
        clients = []
        for impact in impacts:
            if impact.category == "endpoint":
                clients.append(self._client_from_path(impact.path))
        return self._unique_sorted(client for client in clients if client)

    def _recommendations(self, impacts: list[ContractImpactItem]) -> list[str]:
        recommendations = []
        for impact in impacts:
            if impact.is_breaking:
                recommendations.append(
                    f"Review {impact.category} {impact.name}: {impact.change_type} impact may break consumers"
                )
        if not recommendations and impacts:
            recommendations.append("Review non-breaking contract additions for generated client updates")
        if not impacts:
            recommendations.append("No contract consumer impact detected")
        return recommendations

    def _risk_level(self, impacts: list[ContractImpactItem]) -> str:
        severities = {impact.severity for impact in impacts}
        if "critical" in severities:
            return "critical"
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        return "low"

    def _severity_for(self, category: str, change_type: str, is_breaking: bool) -> str:
        if category == "endpoint" and ("removed" in change_type or is_breaking):
            return "critical"
        if is_breaking:
            return "high"
        if category == "endpoint":
            return "medium"
        return "low"

    def _category_from_path(self, path: str) -> str:
        if "paths" in path:
            return "endpoint"
        if "components" in path and "schemas" in path:
            return "schema"
        return "contract"

    def _name_from_path(self, category: str, path: str) -> str:
        if category == "schema":
            parts = [part for part in path.replace("[", ".").replace("]", ".").replace("'", "").split(".") if part]
            if "schemas" in parts:
                schema_index = parts.index("schemas") + 1
                if schema_index < len(parts):
                    return parts[schema_index]
        return path

    def _client_from_path(self, path: str) -> str:
        segments = [segment for segment in path.split("/") if segment and not segment.startswith("{")]
        for segment in segments:
            if segment == "api" or segment.startswith("v") and segment[1:].isdigit():
                continue
            return segment
        return ""

    def _unique_sorted(self, values: Iterable[str]) -> list[str]:
        return sorted({value for value in values if value})

    def _as_mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _as_list(self, value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    def _get_value(self, value: Any, name: str, default: Any) -> Any:
        if isinstance(value, Mapping):
            return value.get(name, default)
        return getattr(value, name, default)
