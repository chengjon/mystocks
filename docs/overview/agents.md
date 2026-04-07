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

> **权威来源声明**:
> 本文件属于 `docs/overview/` 下的概览文档，不是当前仓库规则的唯一事实来源。
> 如与仓库级共享规则或执行入口文档冲突，应始终以 `architecture/STANDARDS.md` 作为共享规则与审批门禁来源，并按职责分别以根目录 `AGENTS.md`、根目录 `CLAUDE.md` 作为执行入口参考。
>
> 涉及迁移收口、兼容层退役、清理/删除判定、审计指标口径时，请统一回到 `architecture/STANDARDS.md`。

> **使用说明**:
> 下文命令、格式、架构示例属于 overview 快照。当前可执行规则、命令与配置数值以根目录 `AGENTS.md` 和 `architecture/STANDARDS.md` 为准。

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
- Use Black formatter; current formatter settings follow root `AGENTS.md` and `pyproject.toml`
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

### Database Architecture
- Current database architecture and migration status must follow root `AGENTS.md` and `architecture/STANDARDS.md`
- Historical notes in this overview must not be treated as authorization to keep or introduce parallel layers
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
from src.storage.database import DatabaseTableManager
```

Historical compatibility import paths may appear in old code or reports, but new changes should follow the canonical paths defined in root `AGENTS.md`.
