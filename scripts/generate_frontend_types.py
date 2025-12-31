#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic models

This script extracts Pydantic model definitions from the backend
and generates corresponding TypeScript interfaces for the frontend.
"""

import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent / "web" / "backend"
sys.path.insert(0, str(backend_path))

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
# Multiple directories to scan for Pydantic models
SCAN_DIRS = [
    PROJECT_ROOT / "web" / "backend" / "app" / "schemas",
    PROJECT_ROOT / "web" / "backend" / "app" / "schema",
    PROJECT_ROOT / "web" / "backend" / "app" / "api",
    PROJECT_ROOT / "web" / "backend" / "app" / "models",
]
OUTPUT_DIR = PROJECT_ROOT / "web" / "frontend" / "src" / "api" / "types"


class TypeConverter:
    """Converts Python types to TypeScript types"""

    # Type mapping from Python to TypeScript
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
        "list": "any[]",
        "dict": "Record<string, any>",
        "Dict": "Record<string, any>",
        "Any": "any",
        "EmailStr": "string",
        "HttpUrl": "string",
        "PyObject": "any",
        "Json": "any",
        "T": "any",
        "False": "false",
        "True": "true",
    }

    @classmethod
    def convert_type(cls, type_str: str) -> str:
        """Convert a Python type string to TypeScript"""
        if not type_str:
            return "any"

        # First handle simple types
        if type_str in cls.TYPE_MAP:
            return cls.TYPE_MAP[type_str]

        # Handle List[...]
        if type_str.startswith("List[") and type_str.endswith("]"):
            inner = type_str[5:-1]
            return f"{cls.convert_type(inner)}[]"

        # Handle Dict[k, v]
        if type_str.startswith("Dict[") and type_str.endswith("]"):
            inner = type_str[5:-1]
            parts = inner.split(",", 1)
            if len(parts) == 2:
                k = cls.convert_type(parts[0].strip())
                v = cls.convert_type(parts[1].strip())
                return f"Record<{k}, {v}>"
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
            return type_str[8:-1].replace(",", " |")

        return type_str

    @classmethod
    def convert_field_name(cls, name: str) -> str:
        """Keep original field name (usually snake_case from backend)"""
        return name


class PydanticModelExtractor:
    """Extract Pydantic model and Enum definitions from Python files"""

    def __init__(self):
        self.models: Dict[str, Dict] = {}

    def extract_from_file(self, file_path: Path) -> None:
        """Extract models from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_pydantic_model(node):
                        model_info = self._extract_model_info(node)
                        if model_info:
                            self.models[node.name] = model_info
                    elif self._is_enum(node):
                        enum_info = self._extract_enum_info(node)
                        if enum_info:
                            self.models[node.name] = enum_info

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _is_pydantic_model(self, class_node: ast.ClassDef) -> bool:
        """Check if a class is a Pydantic model"""
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                return True
        return False

    def _is_enum(self, class_node: ast.ClassDef) -> bool:
        """Check if a class is an Enum"""
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "Enum":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Enum":
                return True
        return False

    def _extract_model_info(self, class_node: ast.ClassDef) -> Dict:
        """Extract model information from a class node"""
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
        """Extract enum values"""
        values = []
        for item in class_node.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1:
                target = item.targets[0]
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if isinstance(item.value, ast.Constant):
                        val = item.value.value
                        if isinstance(val, str):
                            values.append(f"'{val}'")
                        else:
                            values.append(str(val))
        return {"type": "enum", "values": values}

    def _get_type_annotation(self, node) -> str:
        """Recursively extract type annotation as string"""
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
        if isinstance(node, ast.Tuple):
            return ", ".join(self._get_type_annotation(elt) for elt in node.elts)
        if isinstance(node, ast.List):
            return ", ".join(self._get_type_annotation(elt) for elt in node.elts)
        if hasattr(ast, 'unparse'):
            return ast.unparse(node)
        return "any"


class TypeScriptGenerator:
    """Generate TypeScript code from model definitions"""

    def __init__(self):
        self.type_converter = TypeConverter()

    def generate(self, models: Dict[str, Dict]) -> str:
        """Generate TypeScript code from models"""
        output = [
            "// Auto-generated TypeScript types from backend Pydantic models",
            f"// Generated at: {datetime.now().isoformat()}",
            "",
            "// API Response Types"
        ]

        # Generate each model/enum
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

    def _sort_models_by_dependency(self, models: Dict[str, Dict]) -> Dict[str, Dict]:
        """Sort models by dependency order"""
        # Simple implementation - just return sorted by name
        # In production, you'd want to analyze actual dependencies
        return dict(sorted(models.items()))


def main():
    """Main function"""
    print("🔄 Generating TypeScript types from Pydantic models...")

    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Extract models
    extractor = PydanticModelExtractor()

    # Process all Python files in specified directories recursively
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"  ⚠️  Directory not found: {scan_dir}")
            continue

        print(f"  📂 Scanning {scan_dir.relative_to(PROJECT_ROOT)}...")
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                print(f"    Processing {py_file.name}...")
                extractor.extract_from_file(py_file)

    # Generate TypeScript
    generator = TypeScriptGenerator()
    ts_code = generator.generate(extractor.models)

    # Write to output file
    output_file = OUTPUT_DIR / "generated-types.ts"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ts_code)

    print(f"✅ Generated TypeScript types: {output_file}")
    print(f"   Found {len(extractor.models)} models/enums")


if __name__ == "__main__":
    main()
