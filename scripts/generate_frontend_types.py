#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic models

This script extracts Pydantic model definitions from the backend
and generates corresponding TypeScript interfaces for the frontend.
Supports multi-file output organized by domain.

Usage:
    python scripts/generate_frontend_types.py           # Generate all types
    python scripts/generate_frontend_types.py --watch  # Watch mode
    python scripts/generate_frontend_types.py --domain=trading  # Generate specific domain
    python scripts/generate_frontend_types.py --openapi-spec generated_openapi.json
                                                       # Validate CI contract artifact before generation
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
import yaml

try:
    from ._generate_frontend_types_cli import (
        build_argument_parser,
        generate_index_file as _generate_index_file,
        run_generation,
    )
except ImportError:
    from _generate_frontend_types_cli import build_argument_parser, generate_index_file as _generate_index_file, run_generation

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "web" / "frontend" / "src" / "api" / "types"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Domain mapping: which directories belong to which domain
DOMAIN_MAP = {
    "trading": ["trading", "session", "position"],
    "strategy": ["strategy", "indicator", "ml"],
    "system": ["health", "routing", "database"],
    "admin": ["auth", "audit", "optimization"],
    "analysis": ["sentiment", "backtest", "stress_test"],
    "market": ["market", "quote", "kline"],
}

# Directory to domain mapping
DIR_TO_DOMAIN = {
    "v1/trading": "trading",
    "v1/strategy": "strategy",
    "v1/system": "system",
    "v1/admin": "admin",
    "v1/analysis": "analysis",
    "schemas": "common",
    "schema": "common",
    "models": "common", # Explicitly map models directory to common
}


class TypeConverter:
    """Converts Python types to TypeScript types"""

    TYPE_MAP = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "None": "null",
        "NoneType": "null",
        "datetime": "string",
        "date": "string",
        "Decimal": "number",
        "UUID": "string",
        "bytes": "string",
        "dict": "Record<string, unknown>",
        "list": "unknown[]",
        "tuple": "unknown[]",
        "date_type": "string",
    }

    @classmethod
    def convert_type(cls, type_str: str) -> str:
        if not type_str:
            return "unknown"
        type_str = type_str.strip()

        if type_str in cls.TYPE_MAP:
            return cls.TYPE_MAP[type_str]

        # Handle List[...]
        if (type_str.startswith("List[") or type_str.startswith("list[")) and type_str.endswith("]"):
            inner = cls._strip_outer_parentheses(type_str[5:-1])
            converted = cls.convert_type(inner)
            return cls._as_array_type(converted)

        # Handle Dict[...]
        if (type_str.startswith("Dict[") or type_str.startswith("dict[")) and type_str.endswith("]"):
            inner = cls._strip_outer_parentheses(type_str[5:-1])
            parts = cls._split_top_level(inner, ",")
            if len(parts) == 2:
                k = cls.convert_type(parts[0].strip())
                v = cls.convert_type(parts[1].strip())
                result = f"Record<{k}, {v}>"
                return cls._fix_python_type_names(result)
            return "Record<string, unknown>"

        # Handle Optional[...]
        if type_str.startswith("Optional[") and type_str.endswith("]"):
            inner = cls._strip_outer_parentheses(type_str[9:-1])
            return f"{cls.convert_type(inner)} | null"

        # Handle Union[...]
        if type_str.startswith("Union[") and type_str.endswith("]"):
            inner = cls._strip_outer_parentheses(type_str[6:-1])
            parts = [cls.convert_type(p.strip()) for p in cls._split_top_level(inner, ",")]
            return " | ".join(parts)

        # Handle Literal[...]
        if type_str.startswith("Literal[") and type_str.endswith("]"):
            inner = type_str[8:-1]
            # Remove tuple parentheses if present: ('start', 'stop') -> 'start', 'stop'
            inner = re.sub(r"^\(|\)$", "", inner)
            # Split by comma and clean up quotes
            parts = [p.strip().strip("'\"") for p in cls._split_top_level(inner, ",")]
            # Convert to TypeScript union type
            return " | ".join(f"'{part}'" for part in parts)

        # Handle already flattened union expression, such as "(List[float] | List[List[float]])"
        stripped = cls._strip_outer_parentheses(type_str)
        union_parts = cls._split_top_level(stripped, "|")
        if len(union_parts) > 1:
            return " | ".join(cls.convert_type(part.strip()) for part in union_parts)

        # Fix any remaining list[...] patterns (not handled by List[...] above)
        if "list[" in type_str:
            type_str = type_str.replace("list[", "").replace("]", "[]")

        # Apply Python type name fixes at the end
        return cls._fix_python_type_names(type_str)

    @classmethod
    def _as_array_type(cls, ts_type: str) -> str:
        ts_type = ts_type.strip()
        if "|" in ts_type or "&" in ts_type:
            ts_type = f"({ts_type})"
        return f"{ts_type}[]"

    @classmethod
    def _strip_outer_parentheses(cls, value: str) -> str:
        value = value.strip()
        while value.startswith("(") and value.endswith(")") and cls._is_wrapped_by_outer_parens(value):
            value = value[1:-1].strip()
        return value

    @classmethod
    def _is_wrapped_by_outer_parens(cls, value: str) -> bool:
        depth = 0
        for idx, ch in enumerate(value):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
                if depth == 0 and idx != len(value) - 1:
                    return False
        return depth == 0

    @classmethod
    def _split_top_level(cls, value: str, delimiter: str = ",") -> List[str]:
        parts: List[str] = []
        current: List[str] = []
        depth_round = 0
        depth_square = 0
        depth_angle = 0
        depth_curly = 0

        for ch in value:
            if ch == "(":
                depth_round += 1
            elif ch == ")":
                depth_round = max(depth_round - 1, 0)
            elif ch == "[":
                depth_square += 1
            elif ch == "]":
                depth_square = max(depth_square - 1, 0)
            elif ch == "<":
                depth_angle += 1
            elif ch == ">":
                depth_angle = max(depth_angle - 1, 0)
            elif ch == "{":
                depth_curly += 1
            elif ch == "}":
                depth_curly = max(depth_curly - 1, 0)

            if (
                ch == delimiter
                and depth_round == 0
                and depth_square == 0
                and depth_angle == 0
                and depth_curly == 0
            ):
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue

            current.append(ch)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)
        return parts if parts else [value]

    @classmethod
    def _fix_python_type_names(cls, type_str: str) -> str:
        # Fix Python type names in various contexts
        # First remove parentheses around types: (string, any) -> string, any
        type_str = re.sub(r"\(([^,]+),\s*([^)]+)\)", r"\1, \2", type_str)

        # Then handle bare types with word boundaries (but not in generic context)
        # Use negative lookbehind to avoid replacing list when followed by [
        replacements = {
            r"\bstr\b": "string",
            r"\bint\b": "number",
            r"\bfloat\b": "number",
            r"\bbool\b": "boolean",
            r"\bAny\b": "unknown",
            r"\bdict\b": "Record<string, unknown>",
            r"\blist(?!\[)": "Array<unknown>",  # Only replace 'list' when NOT followed by [
        }
        for py_type, ts_type in replacements.items():
            type_str = re.sub(py_type, ts_type, type_str)
        return type_str


class TypeGenerationConfig:
    """Configuration for type generation and conflict resolution"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (PROJECT_ROOT / "scripts" / "type_generation_config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {self.config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            print(f"⚠️  Error loading config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "conflict_resolution": {
                "priority_sources": ["nullable", "latest", "first"],
                "auto_fix_rules": [],
                "ignore_conflicts": ["market", "timestamp", "id"],
            },
            "output": {"warn_on_conflicts": True, "max_warnings": 50, "include_conflict_comments": False},
            "validation": {"strict_mode": False, "required_domains": []},
        }

    def get_priority_sources(self) -> List[str]:
        return self.config.get("conflict_resolution", {}).get("priority_sources", ["nullable", "latest", "first"])

    def get_auto_fix_rules(self) -> List[Dict[str, Any]]:
        return self.config.get("conflict_resolution", {}).get("auto_fix_rules", [])

    def get_ignore_conflicts(self) -> List[str]:
        return self.config.get("conflict_resolution", {}).get("ignore_conflicts", [])

    def should_warn_on_conflicts(self) -> bool:
        return self.config.get("output", {}).get("warn_on_conflicts", True)

    def get_max_warnings(self) -> int:
        return self.config.get("output", {}).get("max_warnings", 50)

    def is_strict_mode(self) -> bool:
        return self.config.get("validation", {}).get("strict_mode", False)

    def get_required_domains(self) -> List[str]:
        return self.config.get("validation", {}).get("required_domains", [])


class PydanticModelExtractor:
    """Extract Pydantic model and Enum definition from Python files"""

    def __init__(self, config: TypeGenerationConfig):
        self.config = config
        self.models: Dict[str, Dict] = {}
        self.domain_models: Dict[str, Dict[str, Dict]] = defaultdict(dict)
        self.type_conflicts: Dict[str, List[Dict]] = defaultdict(list)
        self.warnings: List[str] = []
        self.fixed_conflicts: List[str] = []

    def extract_from_file(self, file_path: Path) -> None:
        """Extract models from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    domain = self._determine_domain(file_path, node.name)
                    if self._is_pydantic_model(node):
                        model_info = self._extract_model_info(node)
                        if model_info:
                            self._add_or_merge_model(node.name, model_info, file_path, domain)
                    elif self._is_enum(node):
                        enum_info = self._extract_enum_info(node)
                        if enum_info:
                            self._add_or_merge_model(node.name, enum_info, file_path, domain)

        except Exception as e:
            print(f"  ⚠️  Error processing {file_path}: {e}")

    def _add_or_merge_model(self, name: str, new_info: Dict, file_path: Path, domain: str) -> None:
        """Add new model or merge with existing one, detecting conflicts"""
        new_info["source_file"] = str(file_path.relative_to(PROJECT_ROOT))
        new_info["source_domain"] = domain
        
        if name in self.models:
            existing_info = self.models[name]
            existing_domain = existing_info.get("source_domain", "common")

            # Prioritize specific domains over 'common'
            if existing_domain == "common" and domain != "common":
                # Reassign the model to the more specific domain
                # Remove from common's domain_models if it was there
                if name in self.domain_models["common"]:
                    del self.domain_models["common"][name]
                self.models[name] = new_info # Update model with the new info (which contains the specific domain)
                self.domain_models[domain][name] = new_info
                self.warnings.append(
                    f"Reassigned model '{name}' from 'common' to '{domain}' due to more specific definition in {file_path}"
                )
                return # Successfully reassigned, no further merging/conflict checks needed for this instance
            elif domain == "common" and existing_domain != "common":
                # If current is common but existing is specific, keep the existing one
                self.warnings.append(
                    f"Ignoring 'common' definition for model '{name}' in {file_path}, keeping definition from '{existing_domain}'"
                )
                return

            # Check for type conflicts
            if existing_info.get("type") != new_info.get("type"):
                conflict_info = {
                    "name": name,
                    "existing": existing_info,
                    "new": new_info,
                    "file_path": str(file_path),
                    "domain": domain,
                }
                self.type_conflicts[name].append(conflict_info)
                self.warnings.append(
                    f"Type conflict for '{name}': existing {existing_info.get('type')} vs new {new_info.get('type')} in {file_path}"
                )

            # Merge interface fields if both are interfaces
            elif existing_info.get("type") == "interface" and new_info.get("type") == "interface":
                merged_fields = self._merge_interface_fields(
                    existing_info.get("fields", {}), new_info.get("fields", {}), name
                )
                existing_info["fields"] = merged_fields
                self.domain_models[domain][name] = existing_info
            else:
                # For non-interface types, keep the first definition and warn
                self.warnings.append(
                    f"Duplicate {new_info.get('type')} definition for '{name}' in {file_path}, keeping first definition"
                )
        else:
            # First occurrence
            self.models[name] = new_info
            self.domain_models[domain][name] = new_info

    def _merge_interface_fields(self, existing_fields: Dict, new_fields: Dict, interface_name: str) -> Dict:
        """Merge fields from two interface definitions, handling type conflicts"""
        merged = existing_fields.copy()

        for field_name, new_field_info in new_fields.items():
            if field_name in merged:
                existing_field_info = merged[field_name]

                # Check for type conflicts in the same field
                existing_field_info = merged[field_name]

                # Check for type conflicts in the same field
                existing_type = existing_field_info.get("type", "")
                new_type = new_field_info.get("type", "")

                if existing_type != new_type:
                    # Try to resolve type conflicts using configuration rules
                    resolved_type = self._resolve_type_conflict(existing_type, new_type, field_name)
                    if resolved_type:
                        merged[field_name] = {
                            "type": resolved_type,
                            "required": existing_field_info.get("required", False),
                        }
                        if resolved_type != existing_type:
                            self.fixed_conflicts.append(
                                f"Auto-fixed type conflict for {interface_name}.{field_name}: '{existing_type}' vs '{new_type}' -> '{resolved_type}'"
                            )
                        else:
                            self.warnings.append(
                                f"Resolved type conflict for {interface_name}.{field_name}: '{existing_type}' vs '{new_type}' -> '{resolved_type}'"
                            )
                    else:
                        # Keep existing type and warn
                        self.warnings.append(
                            f"Unresolved type conflict for {interface_name}.{field_name}: '{existing_type}' vs '{new_type}', keeping '{existing_type}'"
                        )
            else:
                # New field
                merged[field_name] = new_field_info

        return merged

    def _resolve_type_conflict(self, type1: str, type2: str, field_name: str = None) -> Optional[str]:
        """Try to resolve type conflicts using configuration rules"""
        # Check if this field should be ignored
        if field_name and field_name in self.config.get_ignore_conflicts():
            return type1  # Keep first definition for ignored fields

        # Check auto-fix rules from configuration
        for rule in self.config.get_auto_fix_rules():
            pattern = rule.get("pattern", "")
            action = rule.get("action", "")

            # Create regex pattern for matching
            conflict_pattern = f"{re.escape(type1)} vs {re.escape(type2)}|{re.escape(type2)} vs {re.escape(type1)}"
            if re.search(pattern, conflict_pattern, re.IGNORECASE):
                if action == "prefer_nullable":
                    # Prefer nullable versions
                    if "null" in type1 and "null" not in type2:
                        return type1
                    elif "null" in type2 and "null" not in type1:
                        return type2
                    elif "null" in type1 and "null" in type2:
                        return type1  # Both nullable, keep first
                elif action == "prefer_string":
                    if "string" in [type1, type2]:
                        return "string" if "string" in type1 else type2
                elif action == "prefer_any":
                    if "Any" in [type1, type2]:
                        return "Any" if "Any" in type1 else type2
                elif action == "prefer_dict":
                    if "dict" in [type1, type2]:
                        return "dict" if "dict" in type1 else type2

        # Fallback to priority-based resolution
        priority_sources = self.config.get_priority_sources()

        for priority in priority_sources:
            if priority == "nullable":
                # Prefer nullable versions
                if "null" in type1 and "null" not in type2:
                    return type1
                elif "null" in type2 and "null" not in type1:
                    return type2
            elif priority == "latest":
                return type2  # Prefer second (later) definition
            elif priority == "strict":
                # Prefer more specific types (harder to determine, keep as fallback)
                pass

        # If no resolution found, return None (cannot resolve)
        return None

    def _determine_domain(self, file_path: Path, class_name: str) -> str:
        """Determine which domain a model belongs to"""
        path_str = str(file_path)

        # Check directory mapping
        for dir_part, domain in DIR_TO_DOMAIN.items():
            if dir_part in path_str:
                return domain

        # Check filename/classname against domain map
        path_lower = path_str.lower()
        class_lower = class_name.lower()

        for domain, keywords in DOMAIN_MAP.items():
            for keyword in keywords:
                if keyword in path_lower or keyword in class_lower:
                    return domain

        return "common"

    def _is_pydantic_model(self, class_node: ast.ClassDef) -> bool:
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                return True
        return False

    def _is_enum(self, class_node: ast.ClassDef) -> bool:
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "Enum":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Enum":
                return True
        return False

    def _extract_model_info(self, class_node: ast.ClassDef) -> Dict:
        fields = {}
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                if field_name.startswith("_"):
                    continue
                field_type = self._get_type_annotation(item.annotation)
                fields[field_name] = {"type": field_type, "required": True}
        return {"type": "interface", "fields": fields}

    def _extract_enum_info(self, class_node: ast.ClassDef) -> Dict:
        values = []
        for item in class_node.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1:
                target = item.targets[0]
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if isinstance(item.value, ast.Constant):
                        val = item.value.value
                        if isinstance(val, str):
                            values.append(f"'{val}'")
                        elif isinstance(val, bool):
                            values.append(str(val).lower())
                        else:
                            values.append(str(val))
        return {"type": "enum", "values": values}

    def _get_type_annotation(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Tuple):
            return ", ".join(self._get_type_annotation(elt) for elt in node.elts)
        if isinstance(node, ast.Subscript):
            value = self._get_type_annotation(node.value)
            slice_val = self._get_type_annotation(node.slice)
            return f"{value}[{slice_val}]"
        if isinstance(node, ast.Attribute):
            return f"{self._get_type_annotation(node.value)}.{node.attr}"
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "constr":
                    return "string"
                if node.func.id in ("conint", "confloat"):
                    return "number"
            return "unknown"
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        return "unknown"


class TypeScriptGenerator:
    """Generate TypeScript code from model definitions"""

    def __init__(self):
        self.type_converter = TypeConverter()

    def generate(self, models: Dict[str, Dict]) -> str:
        """Generate single file TypeScript code (backward compatible)"""
        output = [
            "// Auto-generated TypeScript types from backend Pydantic models",
            "",
            "// Standard Unified Response Wrapper",
            "export interface UnifiedResponse<TData = unknown> {",
            "  code: string | number;",
            "  message: string;",
            "  data: TData;",
            "  request_id?: string;",
            "  process_time?: string;",
            "  timestamp?: number | string;",
            "}",
            "",
        ]

        for name, info in sorted(models.items()):
            if info["type"] == "interface":
                output.append(f"export interface {name} {{")
                for field_name, field_info in info["fields"].items():
                    ts_type = self.type_converter.convert_type(field_info["type"])
                    output.append(f"  {field_name}?: {ts_type};")
                output.append("}")
            elif info["type"] == "enum":
                if info["values"]:
                    union = " | ".join(info["values"])
                    output.append(f"export type {name} = {union};")
                else:
                    output.append(f"export type {name} = unknown;")
            output.append("")

        return "\n".join(output)

    def generate_domain(self, domain: str, models: Dict[str, Dict]) -> str:
        """Generate TypeScript code for a specific domain"""
        if not models:
            return ""

        output = [
            f"// Auto-generated types for {domain} domain",
            "",
        ]

        if domain == "common":
            output.extend([
                "// Standard Unified Response Wrapper",
                "export interface UnifiedResponse<T = unknown> {",
                "  success: boolean;",
                "  code: number;",
                "  message: string;",
                "  data: T;",
                "  timestamp: string;",
                "  request_id: string;",
                "  process_time?: string;",
                "  errors?: unknown;",
                "}",
                "",
            ])

        for name, info in sorted(models.items()):
            output.extend(self._render_model(name, info))

        return "\n".join(output)

    def _render_model(self, name: str, info: Dict) -> List[str]:
        lines: List[str] = []
        if info["type"] == "interface":
            lines.append(f"export interface {name} {{")
            for field_name, field_info in info["fields"].items():
                ts_type = self.type_converter.convert_type(field_info["type"])
                lines.append(f"  {field_name}?: {ts_type};")
            lines.append("}")
        elif info["type"] == "enum":
            if info["values"]:
                union = " | ".join(info["values"])
                lines.append(f"export type {name} = {union};")
            else:
                lines.append(f"export type {name} = unknown;")
        lines.append("")
        return lines

    def write_common_split_files(self, models: Dict[str, Dict], output_dir: Path) -> int:
        common_dir = output_dir / "common"
        common_dir.mkdir(parents=True, exist_ok=True)

        # 1. 将所有实际类型定义生成到 common/all.ts (手术级隔离)
        all_common_code = self.generate_domain("common", models)
        (common_dir / "all.ts").write_text(all_common_code, encoding="utf-8")

        # 2. 瘦身 common.ts 入口文件
        # 只保留极少量的核心基础接口定义，其他全部外迁
        common_entry_lines = [
            "// MyStocks ArtDeco v3.1 Common Types Entry",
            "",
            "/**",
            " * ⚠️ 警告: 本文件已通过工程红线瘦身。",
            " * 实际类型定义已迁移至 ./common/all.ts",
            " */",
            "",
            "// 核心响应契约 (保留在入口方便查阅)",
            "export interface UnifiedResponse<T = unknown> {",
            "  success: boolean;",
            "  code: number;",
            "  message: string;",
            "  data: T;",
            "  timestamp: string;",
            "  request_id: string;",
            "  process_time?: string;",
            "  errors?: unknown;",
            "}",
            "",
            "// 重定向导出所有业务类型",
            "export * from './common/all';",
            "",
        ]
        (output_dir / "common.ts").write_text("\n".join(common_entry_lines), encoding="utf-8")

        return 1

    def write_generated_types_compat_barrel(self, output_dir: Path) -> None:
        generated_types_lines = [
            "// Auto-generated compatibility barrel for legacy imports",
            "",
            "export * from './index';",
            "",
        ]
        (output_dir / "generated-types.ts").write_text("\n".join(generated_types_lines), encoding="utf-8")


def generate_index_file(domains: List[str]) -> str:
    """Generate index.ts file with unified exports (no duplicates)."""
    return _generate_index_file(domains, OUTPUT_DIR)


def main() -> None:
    args = build_argument_parser().parse_args()
    run_generation(
        args,
        project_root=PROJECT_ROOT,
        output_dir=OUTPUT_DIR,
        config_factory=TypeGenerationConfig,
        extractor_factory=PydanticModelExtractor,
        generator_factory=TypeScriptGenerator,
    )


if __name__ == "__main__":
    main()
