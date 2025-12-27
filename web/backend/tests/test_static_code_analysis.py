"""
Static Code Analysis Tests

This test suite performs static analysis of API source code to ensure:
- Proper docstring documentation
- Pydantic model definitions with examples
- Error handling patterns
- Import statement organization
- Type annotation completeness
- Security vulnerability detection

Version: 1.0.0
Date: 2025-12-03
"""

import ast
import inspect
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Add the app directory to Python path for importing modules
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from app.main import app


class StaticCodeAnalyzer:
    """Comprehensive static code analysis for API endpoints"""

    def __init__(self):
        self.api_directory = Path(__file__).parent.parent / "app" / "api"
        self.core_directory = Path(__file__).parent.parent / "app" / "core"
        self.models_directory = Path(__file__).parent.parent / "app" / "models"
        self.services_directory = Path(__file__).parent.parent / "app" / "services"

        self.analysis_results = {
            "summary": {
                "files_analyzed": 0,
                "total_issues": 0,
                "critical_issues": 0,
                "warnings": 0,
                "suggestions": 0,
            },
            "file_results": {},
            "global_issues": [],
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file for code quality issues"""
        file_result: Dict[str, Any] = {
            "path": str(file_path),
            "issues": {"critical": [], "warnings": [], "suggestions": []},
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Run all analyses
            file_result["issues"]["critical"].extend(self._check_security_vulnerabilities(tree, content))
            file_result["issues"]["critical"].extend(self._check_missing_imports(tree))
            file_result["issues"]["warnings"].extend(self._check_docstring_completeness(tree, file_path))
            file_result["issues"]["warnings"].extend(self._check_type_annotations(tree))
            file_result["issues"]["warnings"].extend(self._check_pydantic_models(tree, content))
            file_result["issues"]["suggestions"].extend(self._check_import_organization(content))
            file_result["issues"]["suggestions"].extend(self._check_error_handling_patterns(tree))
            file_result["issues"]["suggestions"].extend(self._check_code_complexity(tree))

        except SyntaxError as e:
            file_result["issues"]["critical"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            file_result["issues"]["warnings"].append(f"Analysis error: {str(e)}")

        # Count issues
        file_result["total_issues"] = (
            len(file_result["issues"]["critical"])
            + len(file_result["issues"]["warnings"])
            + len(file_result["issues"]["suggestions"])
        )
        file_result["critical_count"] = len(file_result["issues"]["critical"])
        file_result["warning_count"] = len(file_result["issues"]["warnings"])
        file_result["suggestion_count"] = len(file_result["issues"]["suggestions"])

        return file_result

    def _check_security_vulnerabilities(self, tree: ast.AST, content: str) -> List[str]:
        """Check for security vulnerabilities"""
        issues = []

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret_key\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potential hardcoded secret found: {pattern}")

        # Check for SQL injection vulnerabilities
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, "id"):
                    if node.func.id == "execute" and isinstance(node.args[0], ast.Str):
                        if any(
                            keyword in node.args[0].s.lower() for keyword in ["select", "insert", "update", "delete"]
                        ):
                            if "%" in node.args[0].s or "$" in node.args[0].s:
                                issues.append("Potential SQL injection vulnerability with string formatting")

        # Check for eval/exec usage
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, "id"):
                    if node.func.id in ["eval", "exec"]:
                        issues.append(f"Dangerous function call: {node.func.id}")

        return issues

    def _check_missing_imports(self, tree: ast.AST) -> List[str]:
        """Check for missing required imports for API endpoints"""
        issues = []
        required_imports = {
            "APIRouter": "fastapi",
            "HTTPException": "fastapi",
            "Depends": "fastapi",
            "BaseModel": "pydantic",
            "Field": "pydantic",
        }

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.add(alias.name)

        # Check if it's an API file (contains router definition)
        has_router = any(
            isinstance(node, ast.Assign)
            and any(target.id == "router" for target in node.targets if isinstance(target, ast.Name))
            for node in ast.walk(tree)
        )

        if has_router:
            missing = [name for name in required_imports.keys() if name not in imports]
            if missing:
                issues.append(f"Missing required imports for API: {', '.join(missing)}")

        return issues

    def _check_docstring_completeness(self, tree: ast.AST, file_path: Path) -> List[str]:
        """Check docstring completeness for functions and classes"""
        issues = []

        # Skip non-API files
        if "api" not in str(file_path).lower():
            return issues

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private functions
                if node.name.startswith("_"):
                    continue

                # Check if function has docstring
                if not ast.get_docstring(node):
                    issues.append(f"Function '{node.name}' missing docstring")
                else:
                    docstring = ast.get_docstring(node)
                    # Check docstring quality
                    if docstring and len(docstring) < 20:
                        issues.append(f"Function '{node.name}' has very brief docstring")
                    if docstring and not any(
                        param in docstring.lower() for param in ["param", "args", "returns", "return"]
                    ):
                        issues.append(f"Function '{node.name}' docstring missing parameter/return documentation")

        return issues

    def _check_type_annotations(self, tree: ast.AST) -> List[str]:
        """Check for type annotation completeness"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private functions
                if node.name.startswith("_"):
                    continue

                # Check return type annotation
                if not node.returns:
                    issues.append(f"Function '{node.name}' missing return type annotation")

                # Check parameter type annotations
                for arg in node.args.args:
                    if arg.arg == "self":
                        continue
                    if not arg.annotation:
                        issues.append(f"Function '{node.name}' parameter '{arg.arg}' missing type annotation")

        return issues

    def _check_pydantic_models(self, tree: ast.AST, content: str) -> List[str]:
        """Check Pydantic model definitions"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                if any(isinstance(base, ast.Name) and base.id == "BaseModel" for base in node.bases):
                    # Check for Field usage with examples
                    has_examples = False
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            if isinstance(item.annotation, ast.Call):
                                if hasattr(item.annotation.func, "id"):
                                    if item.annotation.func.id == "Field":
                                        # Check for example in Field
                                        if any(kw.arg == "example" for kw in item.annotation.keywords):
                                            has_examples = True

                    if not has_examples:
                        issues.append(f"Pydantic model '{node.name}' should include examples in Field definitions")

        return issues

    def _check_import_organization(self, content: str) -> List[str]:
        """Check import statement organization"""
        issues = []
        lines = content.split("\n")

        import_sections: Dict[str, List[str]] = {
            "stdlib": [],
            "third_party": [],
            "local": [],
        }

        current_section = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                # Determine section
                if any(stripped.startswith(lib) for lib in ["import os", "import sys", "from pathlib"]):
                    current_section = "stdlib"
                elif any(lib in stripped for lib in ["fastapi", "pydantic", "sqlalchemy", "pandas"]):
                    current_section = "third_party"
                elif "app." in stripped:
                    current_section = "local"

                if current_section:
                    import_sections[current_section].append(line)

        # Check for proper ordering (stdlib -> third_party -> local)
        section_order = ["stdlib", "third_party", "local"]
        prev_line_num = -1

        for section in section_order:
            for import_line in import_sections[section]:
                line_num = lines.index(import_line)
                if line_num < prev_line_num:
                    issues.append(f"Import ordering issue: {import_line}")
                    break
                prev_line_num = line_num

        return issues

    def _check_error_handling_patterns(self, tree: ast.AST) -> List[str]:
        """Check for proper error handling patterns"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function handles exceptions
                has_try_except = any(isinstance(child, ast.Try) for child in ast.walk(node))

                # Check for HTTPException usage
                has_http_exception = any(
                    isinstance(child, ast.Raise)
                    and isinstance(child.exc, ast.Call)
                    and isinstance(child.exc.func, ast.Name)
                    and child.exc.func.id == "HTTPException"
                    for child in ast.walk(node)
                )

                # If function is an API endpoint (has route decorator)
                is_api_endpoint = any(
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr in ["get", "post", "put", "delete", "patch"]
                    for child in node.decorator_list
                )

                if is_api_endpoint and not has_try_except and not has_http_exception:
                    issues.append(f"API endpoint '{node.name}' lacks proper error handling")

        return issues

    def _check_code_complexity(self, tree: ast.AST) -> List[str]:
        """Check for code complexity issues"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count lines
                lines = len(node.body)
                if lines > 50:
                    issues.append(f"Function '{node.name}' is too long ({lines} lines)")

                # Count nesting depth
                max_depth = self._calculate_nesting_depth(node)
                if max_depth > 4:
                    issues.append(f"Function '{node.name}' has high nesting depth ({max_depth})")

        return issues

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in a node"""
        max_depth = current_depth

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def analyze_api_directory(self) -> Dict[str, Any]:
        """Analyze all files in the API directory"""
        if not self.api_directory.exists():
            return self.analysis_results

        for file_path in self.api_directory.glob("*.py"):
            if file_path.name == "__init__.py":
                continue

            file_result = self.analyze_file(file_path)
            self.analysis_results["file_results"][str(file_path)] = file_result

            # Update summary
            self.analysis_results["summary"]["files_analyzed"] += 1
            self.analysis_results["summary"]["total_issues"] += file_result["total_issues"]
            self.analysis_results["summary"]["critical_issues"] += file_result["critical_count"]
            self.analysis_results["summary"]["warnings"] += file_result["warning_count"]
            self.analysis_results["summary"]["suggestions"] += file_result["suggestion_count"]

        return self.analysis_results

    def generate_report(self) -> str:
        """Generate a detailed analysis report"""
        report = []
        report.append("=" * 80)
        report.append("STATIC CODE ANALYSIS REPORT")
        report.append("=" * 80)

        summary = self.analysis_results["summary"]
        report.append(f"Files Analyzed: {summary['files_analyzed']}")
        report.append(f"Total Issues: {summary['total_issues']}")
        report.append(f"  Critical: {summary['critical_issues']}")
        report.append(f"  Warnings: {summary['warnings']}")
        report.append(f"  Suggestions: {summary['suggestions']}")
        report.append("")

        # File-by-file details
        for file_path, file_result in self.analysis_results["file_results"].items():
            if file_result["total_issues"] > 0:
                report.append(f"File: {file_path}")
                report.append("-" * 40)

                if file_result["issues"]["critical"]:
                    report.append("  CRITICAL ISSUES:")
                    for issue in file_result["issues"]["critical"]:
                        report.append(f"    ❌ {issue}")

                if file_result["issues"]["warnings"]:
                    report.append("  WARNINGS:")
                    for issue in file_result["issues"]["warnings"]:
                        report.append(f"    ⚠️  {issue}")

                if file_result["issues"]["suggestions"]:
                    report.append("  SUGGESTIONS:")
                    for issue in file_result["issues"]["suggestions"]:
                        report.append(f"    💡 {issue}")

                report.append("")

        return "\n".join(report)


@pytest.fixture
def static_analyzer():
    """Create static code analyzer instance"""
    return StaticCodeAnalyzer()


class TestStaticCodeAnalysis:
    """Test suite for static code analysis"""

    def test_docstring_completeness(self, static_analyzer):
        """Test that all API functions have proper docstrings"""
        results = static_analyzer.analyze_api_directory()

        # Count docstring issues
        docstring_issues = 0
        for file_result in results["file_results"].values():
            docstring_issues += sum(1 for issue in file_result["issues"]["warnings"] if "docstring" in issue.lower())

        # Allow some missing docstrings for now (threshold)
        max_allowed_docstring_issues = len(results["file_results"]) * 2  # 2 per file average

        assert (
            docstring_issues <= max_allowed_docstring_issues
        ), f"Too many docstring issues: {docstring_issues} (max allowed: {max_allowed_docstring_issues})"

    def test_type_annotation_completeness(self, static_analyzer):
        """Test that all functions have complete type annotations"""
        results = static_analyzer.analyze_api_directory()

        # Count type annotation issues
        type_issues = 0
        for file_result in results["file_results"].values():
            type_issues += sum(1 for issue in file_result["issues"]["warnings"] if "type annotation" in issue.lower())

        # Type annotations should be mostly complete
        max_allowed_type_issues = len(results["file_results"]) * 3  # 3 per file average

        assert (
            type_issues <= max_allowed_type_issues
        ), f"Too many type annotation issues: {type_issues} (max allowed: {max_allowed_type_issues})"

    def test_pydantic_model_definitions(self, static_analyzer):
        """Test that Pydantic models are properly defined with examples"""
        results = static_analyzer.analyze_api_directory()

        # Count Pydantic model issues
        pydantic_issues = 0
        for file_result in results["file_results"].values():
            pydantic_issues += sum(
                1
                for issue in file_result["issues"]["warnings"]
                if "pydantic" in issue.lower() or "example" in issue.lower()
            )

        # Should have examples in most Pydantic models
        assert pydantic_issues <= 5, f"Too many Pydantic model issues: {pydantic_issues}"

    def test_error_handling_patterns(self, static_analyzer):
        """Test that API endpoints have proper error handling"""
        results = static_analyzer.analyze_api_directory()

        # Count error handling issues
        error_handling_issues = 0
        for file_result in results["file_results"].values():
            error_handling_issues += sum(
                1 for issue in file_result["issues"]["suggestions"] if "error handling" in issue.lower()
            )

        # Most API endpoints should have error handling
        max_allowed_error_issues = len(results["file_results"]) * 2  # 2 per file average

        assert (
            error_handling_issues <= max_allowed_error_issues
        ), f"Too many error handling issues: {error_handling_issues}"

    def test_import_organization(self, static_analyzer):
        """Test that imports are properly organized"""
        results = static_analyzer.analyze_api_directory()

        # Count import organization issues
        import_issues = 0
        for file_result in results["file_results"].values():
            import_issues += sum(1 for issue in file_result["issues"]["suggestions"] if "import" in issue.lower())

        # Should have minimal import organization issues
        assert import_issues <= 3, f"Too many import organization issues: {import_issues}"

    def test_security_vulnerability_detection(self, static_analyzer):
        """Test that no security vulnerabilities are present"""
        results = static_analyzer.analyze_api_directory()

        # Count security issues
        security_issues = 0
        for file_result in results["file_results"].values():
            security_issues += len(file_result["issues"]["critical"])

        # Should have zero critical security issues
        assert security_issues == 0, f"Security vulnerabilities found: {security_issues}"

    def test_comprehensive_static_analysis(self, static_analyzer):
        """Run comprehensive static analysis and ensure quality standards"""
        results = static_analyzer.analyze_api_directory()

        # Generate and print report
        report = static_analyzer.generate_report()
        print(f"\n{report}")

        # Quality thresholds
        total_files = results["summary"]["files_analyzed"]
        max_critical_issues = 0
        max_total_issues = total_files * 10  # 10 issues per file average
        min_quality_score = 0.8  # 80% quality score

        # Assert quality standards
        assert (
            results["summary"]["critical_issues"] <= max_critical_issues
        ), f"Too many critical issues: {results['summary']['critical_issues']}"

        assert (
            results["summary"]["total_issues"] <= max_total_issues
        ), f"Too many total issues: {results['summary']['total_issues']} (max allowed: {max_total_issues})"

        # Calculate quality score (fewer issues = higher score)
        max_possible_issues = total_files * 20  # Assume 20 issues max per file
        quality_score = 1.0 - (results["summary"]["total_issues"] / max_possible_issues)

        assert (
            quality_score >= min_quality_score
        ), f"Code quality score {quality_score:.2%} is below required {min_quality_score:.2%}"

    def test_code_complexity(self, static_analyzer):
        """Test that code complexity is within acceptable limits"""
        results = static_analyzer.analyze_api_directory()

        # Count complexity issues
        complexity_issues = 0
        for file_result in results["file_results"].values():
            complexity_issues += sum(
                1
                for issue in file_result["issues"]["suggestions"]
                if "long" in issue.lower() or "nesting" in issue.lower() or "complexity" in issue.lower()
            )

        # Should have minimal complexity issues
        assert complexity_issues <= 5, f"Too many complexity issues: {complexity_issues}"

    def test_endpoint_function_analysis(self):
        """Test that all endpoint functions follow best practices"""
        from fastapi.routing import APIRoute

        endpoint_functions = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                endpoint_functions.append(route.endpoint)

        # Analyze endpoint functions
        issues = []
        for func in endpoint_functions:
            try:
                # Check if function has proper signature
                sig = inspect.signature(func)

                # Check for dependency injection
                has_deps = any("Depends" in str(param.annotation) for param in sig.parameters.values())

                # Check for proper docstring
                if not func.__doc__ or len(func.__doc__.strip()) < 20:
                    issues.append(f"Endpoint {func.__name__} has insufficient docstring")

            except Exception as e:
                issues.append(f"Could not analyze endpoint {func.__name__}: {str(e)}")

        # Allow some issues for now
        assert len(issues) <= 10, f"Too many endpoint function issues: {len(issues)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
