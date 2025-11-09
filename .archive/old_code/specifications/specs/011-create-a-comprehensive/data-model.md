# Data Model: Function Classification Manual

**Feature**: MyStocks Function Classification Manual
**Phase**: Phase 1 - Design & Contracts
**Date**: 2025-10-19

## Overview

This document defines the data structures used to represent MyStocks codebase metadata, including modules, classes, functions, dependencies, duplications, and optimization opportunities. These models drive both the manual generation process and the machine-readable JSON metadata output.

## Core Entities

### Module

Represents a single Python source file with all its metadata.

```python
@dataclass
class Module:
    """Complete metadata for a Python module."""

    # Identification
    file_path: str                          # Absolute path to file
    module_name: str                        # Fully qualified module name (e.g., "adapters.akshare_adapter")
    category: CategoryEnum                  # Classification category

    # Contents
    docstring: Optional[str]                # Module-level docstring
    classes: List[ClassMetadata]            # Class definitions
    functions: List[FunctionMetadata]       # Module-level functions
    imports: List[str]                      # Import dependencies

    # Metrics
    lines_of_code: int                      # Total lines (including comments/blanks)
    effective_lines: int                    # Code lines only (excluding comments/blanks)
    last_modified: datetime                 # File modification timestamp

    # Relationships
    depends_on: List[str]                   # Module dependencies (resolved imports)
    used_by: List[str]                      # Reverse dependencies
```

**Example**:
```json
{
  "file_path": "/opt/claude/mystocks_spec/unified_manager.py",
  "module_name": "unified_manager",
  "category": "core",
  "docstring": "Unified data management layer for MyStocks system.",
  "classes": [...],
  "functions": [...],
  "imports": ["core", "data_access", "monitoring"],
  "lines_of_code": 500,
  "effective_lines": 380,
  "last_modified": "2025-10-16T08:00:00Z",
  "depends_on": ["core.DataClassification", "data_access.TDengineDataAccess"],
  "used_by": ["system_demo", "main"]
}
```

### ClassMetadata

Represents a class definition within a module.

```python
@dataclass
class ClassMetadata:
    """Metadata for a Python class."""

    # Identification
    name: str                               # Class name
    qualified_name: str                     # Full path (e.g., "unified_manager.MyStocksUnifiedManager")

    # Documentation
    docstring: Optional[str]                # Class docstring

    # Structure
    base_classes: List[str]                 # Inheritance hierarchy
    methods: List[FunctionMetadata]         # Class methods
    properties: List[PropertyMetadata]      # Properties
    class_variables: List[VariableMetadata] # Class-level variables

    # Characteristics
    is_abstract: bool                       # ABC metaclass or abstract methods
    is_dataclass: bool                      # @dataclass decorator
    is_enum: bool                           # Enum subclass

    # Location
    line_number: int                        # Starting line in source file
    end_line_number: int                    # Ending line
```

**Example**:
```json
{
  "name": "MyStocksUnifiedManager",
  "qualified_name": "unified_manager.MyStocksUnifiedManager",
  "docstring": "Central unified data manager for all data operations.",
  "base_classes": [],
  "methods": [
    {
      "name": "save_data_by_classification",
      "signature": "save_data_by_classification(self, classification: DataClassification, data: pd.DataFrame, table_name: str) -> bool",
      ...
    }
  ],
  "properties": [],
  "class_variables": ["_instance"],
  "is_abstract": false,
  "is_dataclass": false,
  "is_enum": false,
  "line_number": 50,
  "end_line_number": 450
}
```

### FunctionMetadata

Represents a function or method.

```python
@dataclass
class FunctionMetadata:
    """Metadata for a Python function or method."""

    # Identification
    name: str                               # Function name
    signature: str                          # Full signature with type hints

    # Parameters
    parameters: List[Parameter]             # Parameter details
    return_type: Optional[str]              # Return type annotation

    # Documentation
    docstring: Optional[str]                # Function docstring

    # Characteristics
    is_async: bool                          # Async function
    is_method: bool                         # Class method vs module function
    is_static: bool                         # Static method
    is_classmethod: bool                    # Class method
    is_property: bool                       # Property decorator
    decorators: List[str]                   # Applied decorators

    # Body analysis
    body_complexity: int                    # Cyclomatic complexity
    body_tokens: List[str]                  # Tokenized body for similarity
    calls_functions: List[str]              # Functions called within body

    # Location
    line_number: int                        # Starting line
    end_line_number: int                    # Ending line
```

**Example**:
```json
{
  "name": "save_data_by_classification",
  "signature": "save_data_by_classification(self, classification: DataClassification, data: pd.DataFrame, table_name: str) -> bool",
  "parameters": [
    {"name": "self", "type_annotation": null, "default_value": null},
    {"name": "classification", "type_annotation": "DataClassification", "default_value": null},
    {"name": "data", "type_annotation": "pd.DataFrame", "default_value": null},
    {"name": "table_name", "type_annotation": "str", "default_value": null}
  ],
  "return_type": "bool",
  "docstring": "Save data with automatic routing based on classification.",
  "is_async": false,
  "is_method": true,
  "is_static": false,
  "is_classmethod": false,
  "is_property": false,
  "decorators": [],
  "body_complexity": 5,
  "body_tokens": ["if", "classification", "==", "MARKET_DATA", ...],
  "calls_functions": ["get_target_database", "tdengine.save_data"],
  "line_number": 120,
  "end_line_number": 145
}
```

### Parameter

Represents a function parameter.

```python
@dataclass
class Parameter:
    """Function parameter metadata."""

    name: str                               # Parameter name
    type_annotation: Optional[str]          # Type hint (if provided)
    default_value: Optional[str]            # Default value (if provided)
    is_keyword_only: bool                   # Keyword-only parameter
    is_positional_only: bool                # Positional-only parameter
    is_varargs: bool                        # *args parameter
    is_kwargs: bool                         # **kwargs parameter
```

### DuplicationCase

Represents detected code duplication.

```python
@dataclass
class DuplicationCase:
    """Detected code duplication between locations."""

    # Identification
    id: str                                 # Unique ID (hash of locations)

    # Severity
    severity: SeverityEnum                  # CRITICAL, HIGH, MEDIUM, LOW

    # Locations
    locations: List[CodeLocation]           # Where duplication occurs (2+)

    # Similarity metrics
    token_similarity: float                 # 0.0 to 1.0 (difflib ratio)
    ast_similarity: float                   # 0.0 to 1.0 (structural similarity)
    similarity_score: float                 # Combined score

    # Classification
    duplicate_type: DuplicateType           # exact, near, pattern
    pattern_name: Optional[str]             # Detected pattern (e.g., "retry decorator")

    # Recommendations
    recommendation: str                     # Consolidation approach
    estimated_effort: str                   # Time estimate (e.g., "2 hours")
    priority_rank: int                      # Numeric priority (1 = highest)
```

**Example**:
```json
{
  "id": "dup_001",
  "severity": "HIGH",
  "locations": [
    {
      "file_path": "/opt/claude/mystocks_spec/adapters/akshare_adapter.py",
      "start_line": 50,
      "end_line": 75,
      "context": "class AkshareDataSource",
      "snippet": "def _retry_api_call(self, func, max_retries=3):\n    ..."
    },
    {
      "file_path": "/opt/claude/mystocks_spec/adapters/baostock_adapter.py",
      "start_line": 45,
      "end_line": 70,
      "context": "class BaostockDataSource",
      "snippet": "def _retry_api_call(self, func, max_retries=3):\n    ..."
    }
  ],
  "token_similarity": 0.92,
  "ast_similarity": 0.88,
  "similarity_score": 0.90,
  "duplicate_type": "near",
  "pattern_name": "retry decorator pattern",
  "recommendation": "Extract to utils/retry_decorator.py as @retry_decorator(max_attempts=3)",
  "estimated_effort": "1 hour",
  "priority_rank": 3
}
```

### CodeLocation

Represents a specific location in source code.

```python
@dataclass
class CodeLocation:
    """Specific location in source code."""

    file_path: str                          # Absolute file path
    start_line: int                         # Starting line number
    end_line: int                           # Ending line number
    context: Optional[str]                  # Surrounding context (class/function name)
    snippet: str                            # Code excerpt (max 20 lines)
```

### OptimizationOpportunity

Represents an identified optimization or refactoring opportunity.

```python
@dataclass
class OptimizationOpportunity:
    """Identified optimization or refactoring opportunity."""

    # Identification
    id: str                                 # Unique ID
    title: str                              # Short description

    # Classification
    type: OpportunityType                   # performance, architecture, code_quality, security
    priority: PriorityEnum                  # CRITICAL, HIGH, MEDIUM, LOW

    # Description
    current_state: str                      # Current implementation description
    proposed_change: str                    # Recommended improvement
    expected_impact: str                    # Quantified benefit

    # Effort
    estimated_effort: str                   # Time estimate
    effort_hours: float                     # Numeric hours for sorting

    # Scope
    affected_modules: List[str]             # Related file paths
    related_duplications: List[str]         # Related duplication IDs

    # Implementation
    implementation_steps: List[str]         # Step-by-step guide
    testing_strategy: str                   # How to verify
    rollback_plan: str                      # Reversion approach
```

**Example**:
```json
{
  "id": "opt_001",
  "title": "Implement connection pooling for all databases",
  "type": "performance",
  "priority": "CRITICAL",
  "current_state": "Individual connections created per operation in db_manager/database_manager.py. No connection reuse. Potential resource leaks.",
  "proposed_change": "Create singleton connection pools (MySQLConnectionPool, PostgreSQLConnectionPool, TDengineConnectionPool, RedisConnectionPool) with configurable max_size.",
  "expected_impact": "Reduce connection overhead by 70%, improve response time by 30-50ms, prevent connection exhaustion under load.",
  "estimated_effort": "8-12 hours",
  "effort_hours": 10.0,
  "affected_modules": [
    "db_manager/database_manager.py",
    "db_manager/connection_manager.py",
    "data_access/tdengine_access.py",
    "data_access/postgresql_access.py",
    "data_access/mysql_access.py",
    "data_access/redis_access.py"
  ],
  "related_duplications": ["dup_015", "dup_016"],
  "implementation_steps": [
    "1. Create connection pool base class in db_manager/connection_pool.py",
    "2. Implement database-specific pool classes",
    "3. Update DatabaseTableManager to use pools",
    "4. Update all data access classes to request connections from pool",
    "5. Add pool configuration to .env (MAX_MYSQL_CONNECTIONS, etc.)",
    "6. Add pool monitoring metrics"
  ],
  "testing_strategy": "Load testing with 100 concurrent users. Verify connection count stays under pool max_size. Measure latency improvement.",
  "rollback_plan": "Revert to direct connection creation if pool introduces issues. Pool implementation is isolated in connection_pool.py."
}
```

## Enumerations

### CategoryEnum

```python
class CategoryEnum(str, Enum):
    """Module categorization."""
    CORE = "core"                           # Entry points, orchestration, critical business logic
    AUXILIARY = "auxiliary"                 # Data adapters, strategies, backtesting
    INFRASTRUCTURE = "infrastructure"       # DB management, config, ORM
    MONITORING = "monitoring"               # Observability, alerts, metrics
    UTILITY = "utility"                     # Helper functions, decorators, validation
```

### SeverityEnum

```python
class SeverityEnum(str, Enum):
    """Duplication severity level."""
    CRITICAL = "critical"                   # ≥95% similarity, immediate action
    HIGH = "high"                           # 80-94% similarity, should fix soon
    MEDIUM = "medium"                       # 60-79% similarity, consider refactoring
    LOW = "low"                             # 40-59% similarity, review only
```

### PriorityEnum

```python
class PriorityEnum(str, Enum):
    """Optimization priority level."""
    CRITICAL = "critical"                   # Blocks production, fix immediately
    HIGH = "high"                           # Significant impact, plan soon
    MEDIUM = "medium"                       # Worthwhile improvement, schedule
    LOW = "low"                             # Nice to have, backlog
```

### OpportunityType

```python
class OpportunityType(str, Enum):
    """Type of optimization opportunity."""
    PERFORMANCE = "performance"             # Speed, throughput, latency
    ARCHITECTURE = "architecture"           # Design patterns, modularity
    CODE_QUALITY = "code_quality"           # Maintainability, readability
    SECURITY = "security"                   # Vulnerabilities, best practices
```

### DuplicateType

```python
class DuplicateType(str, Enum):
    """Type of code duplication."""
    EXACT = "exact"                         # 100% identical
    NEAR = "near"                           # 80-99% similar (minor variations)
    PATTERN = "pattern"                     # Same pattern, different implementation
```

## Derived Data

### CategoryStatistics

Aggregated statistics per category.

```python
@dataclass
class CategoryStatistics:
    """Statistics for a module category."""

    category: CategoryEnum
    module_count: int
    total_lines: int
    total_classes: int
    total_functions: int
    average_complexity: float
    duplication_count: int
    optimization_count: int
```

### DependencyGraph

Graph representation of module dependencies.

```python
@dataclass
class DependencyGraph:
    """Module dependency graph."""

    nodes: List[GraphNode]                  # All modules
    edges: List[GraphEdge]                  # Dependencies
    circular_dependencies: List[List[str]]  # Detected cycles

@dataclass
class GraphNode:
    """Graph node representing a module."""
    id: str                                 # Module file path
    label: str                              # Module name
    category: CategoryEnum
    metrics: Dict[str, Any]                 # LOC, complexity, etc.

@dataclass
class GraphEdge:
    """Graph edge representing a dependency."""
    source: str                             # Source module ID
    target: str                             # Target module ID
    type: EdgeType                          # imports, inherits, calls
    weight: int                             # Number of references

class EdgeType(str, Enum):
    """Dependency edge type."""
    IMPORTS = "imports"                     # Module import
    INHERITS = "inherits"                   # Class inheritance
    CALLS = "calls"                         # Function call
```

## Validation Rules

### Module Validation

- `file_path` must exist and be absolute
- `module_name` must be valid Python identifier
- `category` must be one of CategoryEnum values
- `lines_of_code` must be > 0
- `effective_lines` must be ≤ `lines_of_code`

### DuplicationCase Validation

- `locations` must have ≥ 2 entries
- `similarity_score` must be in range [0.0, 1.0]
- `token_similarity` and `ast_similarity` must be in range [0.0, 1.0]
- `severity` thresholds must match:
  - CRITICAL: ≥ 95% token AND ≥ 90% AST
  - HIGH: ≥ 80% token AND ≥ 70% AST
  - MEDIUM: ≥ 60% token AND ≥ 50% AST
  - LOW: ≥ 40% token AND ≥ 30% AST

### OptimizationOpportunity Validation

- `effort_hours` must be > 0
- `affected_modules` must have ≥ 1 entry
- `implementation_steps` must have ≥ 1 step
- `expected_impact` should include quantifiable metrics

## JSON Schema

Complete JSON Schema for metadata output is available in `contracts/manual-schema.yaml`.

## State Transitions

### Module Lifecycle

```
[New File Detected]
    ↓
[Parse with AST] → [Extract Metadata] → [Classify Category]
    ↓
[Add to Inventory]
    ↓
[Analyze Dependencies] → [Detect Duplications] → [Identify Optimizations]
    ↓
[Generate Documentation]
    ↓
[Validate Output]
    ↓
[Publish Manual]
```

### Duplication Detection Lifecycle

```
[Extract Functions]
    ↓
[Pairwise Comparison] → [Calculate Token Similarity] + [Calculate AST Similarity]
    ↓
[Classify Severity]
    ↓
[Generate Recommendation]
    ↓
[Rank by Priority]
    ↓
[Output to Duplication Index]
```

## Summary

This data model provides:

✅ **Complete representation** of codebase structure (modules, classes, functions)
✅ **Duplication detection** with severity classification and recommendations
✅ **Optimization tracking** with effort estimates and implementation guides
✅ **Dependency mapping** with cycle detection
✅ **Validation rules** to ensure data quality
✅ **JSON-serializable** for metadata output and tooling integration

All models align with the research decisions in `research.md` and support the manual structure defined in `contracts/manual-schema.yaml`.
