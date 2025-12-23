<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md - Coding Agent Configuration

## Build/Lint/Test Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_specific_module.py

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test function
pytest tests/unit/test_specific_module.py::test_specific_function

# Linting
black .
mypy src/

# Check formatting
black --check .
```

## Code Style Guidelines

### Imports
- Use absolute imports with `src.` prefix: `from src.core import ConfigDrivenTableManager`
- Group imports: standard library, third-party, local imports
- Avoid wildcard imports
- Use explicit imports for clarity

### Formatting
- Use Black formatter with default settings
- Line length: 88 characters (Black default)
- Use double quotes for strings
- Use 4 spaces for indentation

### Types
- Use type hints for all function parameters and return values
- Prefer `from __future__ import annotations` for forward references
- Use Pydantic models for data validation where appropriate

### Naming Conventions
- Classes: PascalCase (`DataManager`)
- Functions/Variables: snake_case (`save_data_by_classification`)
- Constants: UPPER_SNAKE_CASE (`DATABASE_CONFIG`)
- Private members: prefixed with underscore (`_private_method`)

### Error Handling
- Use specific exception types
- Log errors with context before raising
- Implement retry logic for external API calls
- Use context managers for resource management

### Project Structure
- Source code: `src/` directory with standardized imports
- Tests: `tests/` directory mirroring source structure
- Scripts: `scripts/` directory organized by purpose
- Config: `config/` directory for YAML/JSON configs
- Docs: `docs/` directory for documentation

### Database Architecture (Week 3+)
- Dual database: TDengine for high-frequency time-series, PostgreSQL for everything else
- Use `MyStocksUnifiedManager` for automatic routing
- Classification-based methods: `save_data_by_classification()`, `load_data_by_classification()`

### Key Import Patterns
```python
# Core components
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

# Data access
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# Adapters
from src.adapters.akshare_adapter import AkshareDataSource
from src.interfaces import IDataSource

# Database management
from src.db_manager import DatabaseTableManager  # Compatibility layer
# OR
from src.storage.database import DatabaseTableManager  # Direct import
```