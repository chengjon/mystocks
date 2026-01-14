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
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

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
            return type_str  # Keep as-is

        # Apply Python type name fixes at the end
        return cls._fix_python_type_names(type_str)

    @classmethod
    def _fix_python_type_names(cls, type_str: str) -> str:
        # Fix Python type names in various contexts
        replacements = {
            # Handle types inside angle brackets or parentheses
            r"\\(str,": "(string,",
            r"\\(int,": "(number,",
            r"\\(float,": "(number,",
            r"\\(bool,": "(boolean,",
            r"\\(Any\\)": "any",
            r", Any\\)": ", any)",
            # Handle bare types with word boundaries
            r"\\bstr\\b": "string",
            r"\\bint\\b": "number",
            r"\\bfloat\\b": "number",
            r"\\bbool\\b": "boolean",
            r"\\bAny\\b": "any",
            r"\\bdict\\b": "Record<string, any>",
        }
        for py_type, ts_type in replacements.items():
            type_str = re.sub(py_type, ts_type, type_str)
        return type_str


class PydanticModelExtractor:
    """Extract Pydantic model and Enum definition from Python files"""

    def __init__(self):
        self.models: Dict[str, Dict] = {}
        self.domain_models: Dict[str, Dict[str, Dict]] = defaultdict(dict)

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
                            self.models[node.name] = model_info
                            self.domain_models[domain][node.name] = model_info
                    elif self._is_enum(node):
                        enum_info = self._extract_enum_info(node)
                        if enum_info:
                            self.models[node.name] = enum_info
                            self.domain_models[domain][node.name] = enum_info

        except Exception as e:
            print(f"  ⚠️  Error processing {file_path}: {e}")

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
    parser = argparse.ArgumentParser(
        description="Generate TypeScript types from Pydantic models"
    )
    parser.add_argument(
        "--domain", "-d", help="Generate types for specific domain only"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate multi-file output (default)"
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate single file (backward compatible)",
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Watch mode (not implemented)"
    )
    args = parser.parse_args()

    print("🔄 Generating TypeScript types from Pydantic models...")

    # Directories to scan for Pydantic models
    SCAN_DIRS = [
        PROJECT_ROOT / "web" / "backend" / "app" / "schemas",
        PROJECT_ROOT / "web" / "backend" / "app" / "schema",
        PROJECT_ROOT / "web" / "backend" / "app" / "api" / "v1",
        PROJECT_ROOT / "web" / "backend" / "app" / "models",
    ]

    # Extract models
    extractor = PydanticModelExtractor()

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

            common_models = {
                k: v for k, v in extractor.models.items() if k not in used_models
            }
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

    print(f"\n📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
