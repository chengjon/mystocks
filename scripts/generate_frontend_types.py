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
"""

import sys
import re
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from collections import defaultdict
import yaml

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
        "dict": "Record<string, any>",
        "list": "any[]",
        "tuple": "any[]",
    }

    @classmethod
    def convert_type(cls, type_str: str) -> str:
        if not type_str:
            return "any"

        if type_str in cls.TYPE_MAP:
            return cls.TYPE_MAP[type_str]

        # Handle List[...]
        if type_str.startswith("List[") and type_str.endswith("]"):
            inner = type_str[5:-1]
            return f"{cls.convert_type(inner)}[]"

        # Handle Dict[...]
        if type_str.startswith("Dict[") and type_str.endswith("]"):
            inner = type_str[5:-1]
            parts = inner.split(",", 1)
            if len(parts) == 2:
                k = cls.convert_type(parts[0].strip())
                v = cls.convert_type(parts[1].strip())
                result = f"Record<{k}, {v}>"
                return cls._fix_python_type_names(result)
            return "Record<string, any>"

        # Handle Optional[...]
        if type_str.startswith("Optional[") and type_str.endswith("]"):
            inner = type_str[9:-1]
            return f"{cls.convert_type(inner)} | null"

        # Handle Union[...]
        if type_str.startswith("Union[") and type_str.endswith("]"):
            inner = type_str[6:-1]
            parts = [cls.convert_type(p.strip()) for p in inner.split(",")]
            return " | ".join(parts)

        # Handle Literal[...]
        if type_str.startswith("Literal[") and type_str.endswith("]"):
            inner = type_str[8:-1]
            # Remove tuple parentheses if present: ('start', 'stop') -> 'start', 'stop'
            inner = re.sub(r"^\(|\)$", "", inner)
            # Split by comma and clean up quotes
            parts = [p.strip().strip("'\"") for p in inner.split(",")]
            # Convert to TypeScript union type
            return " | ".join(f"'{part}'" for part in parts)

        # Apply Python type name fixes at the end
        return cls._fix_python_type_names(type_str)

    @classmethod
    def _fix_python_type_names(cls, type_str: str) -> str:
        # Fix Python type names in various contexts
        # First remove parentheses around types: (string, any) -> string, any
        type_str = re.sub(r"\(([^,]+),\s*([^)]+)\)", r"\1, \2", type_str)

        # Then handle bare types with word boundaries
        replacements = {
            r"\bstr\b": "string",
            r"\bint\b": "number",
            r"\bfloat\b": "number",
            r"\bbool\b": "boolean",
            r"\bAny\b": "any",
            r"\bdict\b": "Record<string, any>",
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
        if name in self.models:
            existing_info = self.models[name]

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
            return "any"
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        return "any"


class TypeScriptGenerator:
    """Generate TypeScript code from model definitions"""

    def __init__(self):
        self.type_converter = TypeConverter()

    def generate(self, models: Dict[str, Dict]) -> str:
        """Generate single file TypeScript code (backward compatible)"""
        output = [
            "// Auto-generated TypeScript types from backend Pydantic models",
            f"// Generated at: {datetime.now().isoformat()}",
            "",
            "// Standard Unified Response Wrapper",
            "export interface UnifiedResponse<TData = any> {",
            "  code: string | number;",
            "  message: string;",
            "  data: TData;",
            "  request_id?: string;",
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
                    output.append(f"export type {name} = any;")
            output.append("")

        return "\n".join(output)

    def generate_domain(self, domain: str, models: Dict[str, Dict]) -> str:
        """Generate TypeScript code for a specific domain"""
        if not models:
            return ""

        output = [
            f"// Auto-generated types for {domain} domain",
            f"// Generated at: {datetime.now().isoformat()}",
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
                    output.append(f"export type {name} = any;")
            output.append("")

        return "\n".join(output)


def generate_index_file(domains: List[str]) -> str:
    """Generate index.ts file with unified exports"""
    lines = [
        "// Auto-generated index file for TypeScript types",
        f"// Generated at: {datetime.now().isoformat()}",
        "",
    ]

    # Export common types first
    common_file = OUTPUT_DIR / "common.ts"
    if common_file.exists():
        lines.append("// Common types")
        lines.append("export * from './common';")
        lines.append("")

    # Export domain types
    for domain in sorted(domains):
        domain_file = OUTPUT_DIR / f"{domain}.ts"
        if domain_file.exists():
            lines.append(f"// {domain.title()} domain types")
            lines.append(f"export * from './{domain}';")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate TypeScript types from Pydantic models")
    parser.add_argument("--domain", "-d", help="Generate types for specific domain only")
    parser.add_argument("--all", action="store_true", help="Generate multi-file output (default)")
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate single file (backward compatible)",
    )
    parser.add_argument("--watch", "-w", action="store_true", help="Watch mode (not implemented)")
    args = parser.parse_args()

    print("🔄 Generating TypeScript types from Pydantic models...")

    # Directories to scan for Pydantic models
    SCAN_DIRS = [
        PROJECT_ROOT / "web" / "backend" / "app" / "schemas",
        PROJECT_ROOT / "web" / "backend" / "app" / "schema",
        PROJECT_ROOT / "web" / "backend" / "app" / "api" / "v1",
        PROJECT_ROOT / "web" / "backend" / "app" / "models",
    ]

    # Load configuration
    config = TypeGenerationConfig()

    # Extract models
    extractor = PydanticModelExtractor(config)

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"  ⚠️  Directory not found: {scan_dir}")
            continue

        print(f"  📂 Scanning {scan_dir.relative_to(PROJECT_ROOT)}...")
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                extractor.extract_from_file(py_file)

    # Generate output
    generator = TypeScriptGenerator()

    if args.single:
        # Generate single file (backward compatible)
        ts_code = generator.generate(extractor.models)
        output_file = OUTPUT_DIR / "generated-types.ts"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ts_code)
        print(f"✅ Generated single file: {output_file}")
    else:
        # Generate multi-file output organized by domain
        domains = set(extractor.domain_models.keys())
        generated_domains = []

        for domain in sorted(domains):
            models = extractor.domain_models[domain]
            if models:
                ts_code = generator.generate_domain(domain, models)
                domain_file = OUTPUT_DIR / f"{domain}.ts"
                with open(domain_file, "w", encoding="utf-8") as f:
                    f.write(ts_code)
                print(f"  ✅ Generated {domain}.ts ({len(models)} models)")
                generated_domains.append(domain)

        # Generate common types for models without domain
        if "common" in domains or extractor.models:
            # Include remaining models in common
            used_models = set()
            for domain_models in extractor.domain_models.values():
                used_models.update(domain_models.keys())

            common_models = {k: v for k, v in extractor.models.items() if k not in used_models}
            if common_models:
                ts_code = generator.generate_domain("common", common_models)
                common_file = OUTPUT_DIR / "common.ts"
                with open(common_file, "w", encoding="utf-8") as f:
                    f.write(ts_code)
                print(f"  ✅ Generated common.ts ({len(common_models)} models)")
                generated_domains.append("common")

        # Generate index file
        index_code = generate_index_file(generated_domains)
        index_file = OUTPUT_DIR / "index.ts"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_code)
        print(f"  ✅ Generated index.ts")

        print(f"\n📊 Summary:")
        print(f"   Total models: {len(extractor.models)}")
        print(f"   Domains: {', '.join(generated_domains)}")

    # Report results
    if extractor.fixed_conflicts:
        print(f"\n✅ {len(extractor.fixed_conflicts)} conflicts auto-fixed:")
        for fix in extractor.fixed_conflicts[:10]:  # Show first 10 fixes
            print(f"    • {fix}")
        if len(extractor.fixed_conflicts) > 10:
            print(f"    • ... and {len(extractor.fixed_conflicts) - 10} more fixes")

    if extractor.warnings:
        max_warnings = config.get_max_warnings()
        print(f"\n⚠️  {len(extractor.warnings)} warnings detected:")
        for warning in extractor.warnings[:max_warnings]:  # Show configured number of warnings
            print(f"    • {warning}")
        if len(extractor.warnings) > max_warnings:
            print(f"    • ... and {len(extractor.warnings) - max_warnings} more warnings (limited by config)")

    if extractor.type_conflicts and config.should_warn_on_conflicts():
        print(f"\n🚨 {len(extractor.type_conflicts)} type conflicts detected:")
        for name, conflicts in extractor.type_conflicts.items():
            print(f"    • {name}: {len(conflicts)} conflicting definitions")

    # Check for strict mode
    if config.is_strict_mode() and (extractor.warnings or extractor.type_conflicts):
        print(f"\n❌ Strict mode enabled - exiting with error due to conflicts/warnings")
        sys.exit(1)

    print(f"\n📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
