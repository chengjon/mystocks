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
SCHEMAS_DIR = PROJECT_ROOT / "web" / "backend" / "app" / "schemas"
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
        "datetime": "string",
        "date": "string",
        "Decimal": "string",
        "UUID": "string",
        "bytes": "string",
    }

    # Complex type patterns
    COMPLEX_PATTERNS = {
        r"List\[(.+?)\]": r"\1[]",
        r"Optional\[(.+?)\]": r"\1 | null",
        r"Union\[(.+?)\]": r"\1",
        r"Dict\[(.+?),\s*(.+?)\]": r"Record<\1, \2>",
        r"Set\[(.+?)\]": r"Set<\1>",
        r"Tuple\[(.+?)\]": r"[\1]",
        r"Literal\[(.+?)\]": r"\1",
        r"Any": "any",
        "object": "any",
    }

    @classmethod
    def convert_type(cls, type_str: str) -> str:
        """Convert a Python type string to TypeScript"""
        # First handle simple types
        if type_str in cls.TYPE_MAP:
            return cls.TYPE_MAP[type_str]

        # Handle complex types with regex
        for pattern, replacement in cls.COMPLEX_PATTERNS.items():
            type_str = re.sub(pattern, replacement, type_str)

        # Handle union types
        if " | " in type_str:
            parts = type_str.split(" | ")
            # Convert each part individually
            converted_parts = [cls.convert_type(part.strip()) for part in parts]
            return " | ".join(converted_parts)

        return type_str

    @classmethod
    def convert_field_name(cls, name: str) -> str:
        """Convert snake_case to camelCase"""
        if not name:
            return name

        # Don't convert already camelCase or constants
        if name.isupper() or "_" not in name:
            return name

        parts = name.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])


class PydanticModelExtractor:
    """Extract Pydantic model definitions from Python files"""

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
                    # Check if it's a Pydantic model
                    if self._is_pydantic_model(node, content):
                        model_info = self._extract_model_info(node, content)
                        if model_info:
                            self.models[node.name] = model_info

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _is_pydantic_model(self, class_node: ast.ClassDef, content: str) -> bool:
        """Check if a class is a Pydantic model"""
        # Check inheritance from BaseModel
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                return True

        # Check for @validate_arguments decorator
        if any(
            isinstance(d, ast.Name) and d.id == "validate_arguments"
            for d in class_node.decorator_list
        ):
            return True

        return False

    def _extract_model_info(
        self, class_node: ast.ClassDef, content: str
    ) -> Optional[Dict]:
        """Extract model information from a class node"""
        fields = {}
        field_comments = {}

        # Extract field comments
        lines = content.split("\n")
        class_start = class_node.lineno - 1

        # Simple field extraction
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                field_type = self._get_type_annotation(item.annotation)
                default_value = self._get_default_value(item)

                # Skip private/internal fields
                if field_name.startswith("_"):
                    continue

                fields[field_name] = {
                    "type": field_type,
                    "default": default_value,
                    "required": default_value is None,
                }

        return {"fields": fields}

    def _get_type_annotation(self, annotation) -> str:
        """Get type annotation as string"""
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
            elif isinstance(annotation, ast.Subscript):
                value = self._get_type_annotation(annotation.value)
                if hasattr(annotation, "slice"):
                    slice_val = self._get_type_annotation(annotation.slice)
                    return f"{value}[{slice_val}]"
                return f"{value}[...]"
            else:
                return (
                    ast.unparse(annotation)
                    if hasattr(ast, "unparse")
                    else str(annotation)
                )
        except:
            return "any"

    def _get_default_value(self, node) -> Optional[str]:
        """Get default value from an AnnAssign node"""
        if hasattr(node, "value") and node.value:
            if isinstance(node.value, ast.Constant):
                return repr(node.value.value)
            elif isinstance(node.value, ast.List):
                return "[]"
            elif isinstance(node.value, ast.Dict):
                return "{}"
            elif isinstance(node.value, ast.Call):
                if hasattr(node.value.func, "id") and node.value.func.id == "Field":
                    # Check for default in Field()
                    for keyword in node.value.keywords:
                        if keyword.arg == "default":
                            if hasattr(keyword.value, "value"):
                                return repr(keyword.value.value)
                    return None  # Field without default means required
        return None


class TypeScriptGenerator:
    """Generate TypeScript interfaces from model definitions"""

    def __init__(self):
        self.type_converter = TypeConverter()
        self.imports: Set[str] = set()
        self.interfaces: List[str] = []

    def generate(self, models: Dict[str, Dict]) -> str:
        """Generate TypeScript code from models"""
        self.imports.clear()
        self.interfaces.clear()

        # Sort models by dependency
        sorted_models = self._sort_models_by_dependency(models)

        # Generate each model
        for model_name, model_info in sorted_models.items():
            interface = self._generate_interface(model_name, model_info)
            if interface:
                self.interfaces.append(interface)

        # Combine imports and interfaces
        output = ["// Auto-generated TypeScript types from backend Pydantic models"]
        output.append(f"// Generated at: {datetime.now().isoformat()}")
        output.append("")

        # Add common imports if needed
        if self.imports:
            output.append("// Common imports")
            for imp in sorted(self.imports):
                output.append(f"export {imp}")
            output.append("")

        # Add all interfaces
        output.append("// API Response Types")
        output.extend(self.interfaces)

        return "\n".join(output)

    def _generate_interface(self, model_name: str, model_info: Dict) -> str:
        """Generate a TypeScript interface for a model"""
        fields = model_info.get("fields", {})
        if not fields:
            return None

        interface_lines = [f"export interface {model_name} {{", ""]

        # Generate each field
        for field_name, field_info in fields.items():
            ts_field_name = self.type_converter.convert_field_name(field_name)
            ts_type = self.type_converter.convert_type(field_info["type"])

            # Add optional marker if not required
            optional = "?" if field_info["required"] else ""
            comment = (
                f" // Default: {field_info['default']}" if field_info["default"] else ""
            )

            interface_lines.append(f"  {ts_field_name}{optional}: {ts_type};{comment}")

        interface_lines.append("}")
        interface_lines.append("")

        return "\n".join(interface_lines)

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

    # Process all Python files in schemas directory
    for py_file in SCHEMAS_DIR.glob("*.py"):
        if py_file.name != "__init__.py":
            print(f"  Processing {py_file.name}...")
            extractor.extract_from_file(py_file)

    # Generate TypeScript
    generator = TypeScriptGenerator()
    ts_code = generator.generate(extractor.models)

    # Write to output file
    output_file = OUTPUT_DIR / "generated-types.ts"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ts_code)

    print(f"✅ Generated TypeScript types: {output_file}")
    print(f"   Found {len(extractor.models)} models")
    print(f"   Generated {len(generator.interfaces)} interfaces")


if __name__ == "__main__":
    main()
