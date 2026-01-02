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
        "date_type": "string",  # datetime.date alias
        "Decimal": "number",
        "UUID": "string",
        "bytes": "string",
        # Handle Python built-in types
        "dict": "Record<string, any>",
        "date_type": "string | Date",
        "list": "any[]",
        "tuple": "any[]",
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
            literal_content = type_str[8:-1]
            # Check if it's a string literal (single or double quoted)
            if literal_content.startswith("'") or literal_content.startswith('"'):
                # It's a string literal, keep it as-is
                return literal_content
            else:
                # It might be multiple values or other literals
                # Try to parse and quote string values
                try:
                    # Remove outer quotes if present and split by comma
                    cleaned = literal_content.strip("'\"")
                    if "," in cleaned:
                        parts = [p.strip().strip("'\"") for p in cleaned.split(",")]
                        quoted_parts = []
                        for part in parts:
                            # Check if it looks like a string (not a number or boolean)
                            if part in ["True", "False"]:
                                quoted_parts.append(part.lower())
                            elif part.isdigit() or part.replace(".", "").isdigit():
                                quoted_parts.append(part)
                            else:
                                # It's a string literal, add quotes
                                quoted_parts.append(f"'{part}'")
                        return " | ".join(quoted_parts)
                    else:
                        # Single value literal, return as-is
                        return f"'{cleaned}'"
                except Exception:
                    # If parsing fails, return original literal content
                    return literal_content

        # Handle complex nested types with iterative processing
        original = type_str
        while True:
            original = type_str

            # Handle List/Array types - use greedy match for nested types
            if "List[" in type_str:
                # Count brackets to find the matching closing bracket
                while "List[" in type_str:
                    start = type_str.find("List[")
                    depth = 0
                    end = start + 5  # Start after 'List['
                    for i, char in enumerate(type_str[start + 5 :], start=start + 5):
                        if char == "[":
                            depth += 1
                        elif char == "]":
                            if depth == 0:
                                end = i
                                break
                            depth -= 1
                    # Extract the content and replace
                    inner = type_str[start + 5 : end]
                    type_str = type_str[:start] + inner + "[]" + type_str[end + 1 :]

            # Handle Set types
            if "Set[" in type_str or "Set<" in type_str:
                type_str = re.sub(r"Set\[(.+?)\]", r"Set<\1>", type_str)

            # Handle Optional/Union types - match brackets properly
            if "Union[" in type_str:
                while "Union[" in type_str:
                    start = type_str.find("Union[")
                    depth = 0
                    end = -1
                    for i, char in enumerate(type_str[start + 6 :], start=start + 6):
                        if char == "[":
                            depth += 1
                        elif char == "]":
                            if depth == 0:
                                end = i
                                break
                            depth -= 1
                    if end != -1:
                        inner = type_str[start + 6 : end]
                        type_str = type_str[:start] + inner + type_str[end + 1 :]
                    else:
                        break
            if "Optional[" in type_str:
                while "Optional[" in type_str:
                    start = type_str.find("Optional[")
                    depth = 0
                    end = -1
                    for i, char in enumerate(type_str[start + 9 :], start=start + 9):
                        if char == "[":
                            depth += 1
                        elif char == "]":
                            if depth == 0:
                                end = i
                                break
                            depth -= 1
                    if end != -1:
                        inner = type_str[start + 9 : end]
                        type_str = type_str[:start] + inner + " | null" + type_str[end + 1 :]
                    else:
                        break

            # If no changes, we're done
            if type_str == original:
                break

        # Fix Python type names
        type_str = cls._fix_python_type_names(type_str)

        # Handle union types with |
        if " | " in type_str:
            parts = type_str.split(" | ")
            converted_parts = [cls.convert_type(part.strip()) for part in parts]
            return " | ".join(converted_parts)

        return type_str

    @classmethod
    def _fix_python_type_names(cls, type_str: str) -> str:
        """Fix Python type names in generated TypeScript code"""
        # Replace Python type names with TypeScript equivalents
        replacements = {
            r"\bstr\b": "string",
            r"\bint\b": "number",
            r"\bfloat\b": "number",
            r"\bbool\b": "boolean",
            r"\bAny\b": "any",  # Python typing.Any -> TypeScript any
            r"\bdict\b": "Record<string, any>",  # Python dict -> TypeScript Record
            r"\bdate_type\b": "string | Date",  # Python date_type -> Date
        }

        for py_type, ts_type in replacements.items():
            type_str = re.sub(py_type, ts_type, type_str)

        # Fix ast.unparse() adding parentheses around type names
        # e.g., Record<(string, any)> -> Record<string, any>
        type_str = re.sub(r"\(([^)]+)\)", r"\1", type_str)

        # Fix Record types with missing closing >
        # Record<string, any[>  -> Record<string, any[]>
        type_str = re.sub(r"Record<([^>]+)\[>", r"Record<\1[]", type_str)

        # Fix malformed array syntax
        type_str = re.sub(r"\[>;", "[];", type_str)  # [...[>;  -> [...[];
        # Fix Record types with missing closing >
        # Record<string, any[>  -> Record<string, any[]>
        type_str = re.sub(r"Record<([^>]+)\[>", r"Record<\1[]", type_str)

        # Fix standalone 'T' type parameter (generic) -> 'any'
        type_str = re.sub(r"\bT\b", "any", type_str)

        # Fix any remaining dict[] patterns (dict followed by [])
        type_str = re.sub(r"dict\[\]", "Record<string, any>[]", type_str)

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
                        elif isinstance(val, bool):
                            # Convert Python True/False to TypeScript true/false
                            values.append(str(val).lower())
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
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        return "any"


class TypeScriptGenerator:
    """Generate TypeScript code from model definitions"""

    def __init__(self):
        self.type_converter = TypeConverter()
        self.interfaces = []
        self.types = []

    def generate(self, models: Dict[str, Dict]) -> str:
        """Generate TypeScript code from models"""
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
            "// API Response Types",
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

        # Post-process to fix any remaining syntax issues
        ts_code = "\n".join(output)
        ts_code = self._fix_common_syntax_issues(ts_code)

        return ts_code

    def _fix_common_syntax_issues(self, ts_code: str) -> str:
        """Fix common TypeScript syntax issues in generated code"""
        original = ts_code

        # Fix array types with malformed syntax
        # Record<string, any[>;  -> Record<string, any>[];
        ts_code = re.sub(r"\[>;", "[];", ts_code)

        # Fix extra closing brackets
        # ...[]];  -> ...[];
        ts_code = re.sub(r"\[\]\];", r"[];", ts_code)

        # Fix Record<(type, ...)> -> Record<type, ...>
        ts_code = re.sub(r"Record<\(([^)]+)\)", r"Record<\1", ts_code)

        # Fix complex array/union patterns
        # type[ | null]>;  -> type[] | null;
        ts_code = re.sub(r"\[ \| null\]>;", "[] | null;", ts_code)

        # Fix any remaining parentheses around type names
        ts_code = re.sub(r"\(([^()]+)\)", r"\1", ts_code)

        # Fix Python dict[] patterns
        ts_code = re.sub(r"dict\[\]", "Record<string, any>[]", ts_code)
        ts_code = re.sub(r":\s*dict(;|,|\s)", ": Record<string, any>\1", ts_code)

        # Fix standalone T type parameter -> any
        ts_code = re.sub(r":\s*T\b", ": any", ts_code)

        # Fix APIResponse interface to be generic
        # Change "export interface APIResponse {" to "export interface APIResponse<T = any> {"
        # Only if it has "data: T | null" field
        ts_code = re.sub(
            r"export interface APIResponse\s*\{[^}]*data:\s*T\s*\|\s*null",
            "export interface APIResponse<T = any> {\n  success: boolean;\n  code: number;\n  message: string;\n  data: T | null",
            ts_code,
        )

        # Fix PaginatedResponse to be generic
        ts_code = re.sub(
            r"export interface PaginatedResponse\s*\{[^}]*data\?\:\s*dict\[\]",
            "export interface PaginatedResponse<T = any> {\n  total?: number;\n  page?: number;\n  pageSize?: number;\n  data?: T[]",
            ts_code,
        )

        # Debug: print if changes were made
        if ts_code != original:
            print(f"  🔧 Fixed syntax issues ({len(original) - len(ts_code)} chars removed)")

        return ts_code

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

            # Fix common type syntax issues in the generated type string
            ts_type = self._fix_field_type(ts_type)

            # Add optional marker if not required
            optional = "?" if field_info["required"] else ""
            comment = f" // Default: {field_info['default']}" if field_info["default"] else ""

            interface_lines.append(f"  {ts_field_name}{optional}: {ts_type};{comment}")

        interface_lines.append("}")
        interface_lines.append("")

        return "\n".join(interface_lines)

    def _fix_field_type(self, type_str: str) -> str:
        """Fix type string syntax issues"""
        # Fix malformed array syntax
        # type[>;  -> type[];
        type_str = re.sub(r"\[>;", "[];", type_str)

        # Fix type[ | null]>;  -> type[] | null;
        type_str = re.sub(r"\[ \| null\]>;", "[] | null;", type_str)

        # Fix parentheses around type names
        type_str = re.sub(r"\(([^()]+)\)", r"\1", type_str)

        return type_str

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

    # Custom types to append (not overwritten by generator)
    custom_types = """
// ============================================
// Custom Type Aliases (appended by generator)
// ============================================

// Common type aliases for Python backend types
export type Dict = Record<string, any>;
export type EmailStr = string;

// Type alias for backward compatibility
export type KLineDataResponse = KlineResponse;

// API wrapper response type for FundFlow (inner data structure)
export interface FundFlowAPIResponse {
  fundFlow?: FundFlowItem[];
  total?: number;
  symbol?: string | null;
  timeframe?: string | null;
}

// Full API response wrapper for FundFlow (with success/code/message)
export interface FundFlowFullResponse {
  success?: boolean;
  code?: number;
  message?: string;
  data?: FundFlowAPIResponse | null;
  timestamp?: string;
  request_id?: string;
  errors?: any;
}

// Index data for market overview
export interface IndexData {
  code?: string;
  name?: string;
  current?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  timestamp?: string;
}

// Sector data for market heatmap
export interface SectorData {
  name?: string;
  changePercent?: number;
  stockCount?: number;
  leadingStock?: string | null;
  avgPrice?: number;
}

// K-line point for chart data
export interface KLinePoint {
  time?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

// Stock search result
export interface StockSearchResult {
  symbol?: string;
  name?: string;
  market?: string;
  type?: string;
  current?: number;
  change?: number;
  changePercent?: number;
}

// Indicator parameter type
export interface IndicatorParameter {
  name?: string;
  type?: string;
  default?: any;
  min?: number;
  max?: number;
  step?: number;
}

// System status response
export interface SystemStatusResponse {
  status?: string;
  version?: string;
  uptime?: number;
  cpu?: number;
  memory?: number;
  disk?: number;
  components?: Record<string, any>;
  timestamp?: string;
}

// Monitoring alert response
export interface MonitoringAlertResponse {
  alerts?: MonitoringAlert[];
  totalCount?: number;
}

export interface MonitoringAlert {
  id?: number;
  severity?: string;
  message?: string;
  timestamp?: string;
  acknowledged?: boolean;
}

// Log entry response
export interface LogEntryResponse {
  logs?: LogEntry[];
  totalCount?: number;
}

export interface LogEntry {
  level?: string;
  message?: string;
  timestamp?: string;
  source?: string;
}

// Data quality response
export interface DataQualityResponse {
  checks?: DataQualityCheck[];
  summary?: Record<string, any>;
}

export interface DataQualityCheck {
  checkName?: string;
  status?: string;
  message?: string;
  details?: Record<string, any>;
}
"""

    # Write to output file (generated types + custom types)
    output_file = OUTPUT_DIR / "generated-types.ts"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ts_code)
        f.write(custom_types)

    print(f"✅ Generated TypeScript types: {output_file}")
    print(f"   Found {len(extractor.models)} models/enums")


if __name__ == "__main__":
    main()
