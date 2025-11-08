# 📚 MyStocks Documentation Guide

**Last Updated**: 2025-11-08
**Version**: 1.0

This guide helps you navigate the MyStocks project documentation and understand the file organization methodology.

---

## 🎯 Quick Start

**New to the project?** Start here:

1. **[README.md](./README.md)** - Project overview, architecture, and features
2. **[QUICKSTART.md](./docs/guides/QUICKSTART.md)** - Quick setup and first steps
3. **[CLAUDE.md](./CLAUDE.md)** - AI development integration guide

**For developers:**
- **[File Organization Rules](#file-organization-methodology)** - Learn the file placement methodology
- **[scripts/README.md](./scripts/README.md)** - Script organization guide
- **[docs/DOCUMENTATION_STRUCTURE.md](./docs/DOCUMENTATION_STRUCTURE.md)** - Complete documentation inventory

---

## 📖 Core Documentation

### Root Level (Essential Files)

| File | Purpose | Audience |
|------|---------|----------|
| [README.md](./README.md) | Project overview, architecture, setup | All users |
| [CLAUDE.md](./CLAUDE.md) | Claude Code integration guide | AI-assisted developers |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and changes | All users |
| [requirements.txt](./requirements.txt) | Python dependencies | Developers, DevOps |
| [.mcp.json](./.mcp.json) | MCP server configuration | Claude Code users |

### Documentation Categories

#### User & Developer Guides ([docs/guides/](./docs/guides/))

- **[QUICKSTART.md](./docs/guides/QUICKSTART.md)** - Getting started guide
- **[IFLOW.md](./docs/guides/IFLOW.md)** - Development workflow documentation

#### Archived Documentation ([docs/archived/](./docs/archived/))

Old documentation preserved for reference:
- **[START_HERE.md](./docs/archived/START_HERE.md)** - Old entry point (use README.md instead)
- **[TASKMASTER_START_HERE.md](./docs/archived/TASKMASTER_START_HERE.md)** - Old TaskMaster guide (use .taskmaster/CLAUDE.md instead)

#### Configuration Files ([config/](./config/))

All system configuration in one place:
- **[mystocks_table_config.yaml](./config/mystocks_table_config.yaml)** - Database table definitions
- **[docker-compose.tdengine.yml](./config/docker-compose.tdengine.yml)** - TDengine Docker setup
- **[pytest.ini](./config/pytest.ini)** - Test configuration
- **[.readthedocs.yaml](./config/.readthedocs.yaml)** - Documentation build config

#### Scripts ([scripts/](./scripts/))

Organized by functionality. See **[scripts/README.md](./scripts/README.md)** for details:

- **[scripts/tests/](./scripts/tests/)** - All test files (test_*.py)
- **[scripts/runtime/](./scripts/runtime/)** - Production runtime scripts
- **[scripts/database/](./scripts/database/)** - Database operations
- **[scripts/dev/](./scripts/dev/)** - Development utilities

#### Reports ([reports/](./reports/))

Generated analysis and assessment files:
- Database assessments
- Query analysis
- Integration inventories

---

## 🔧 File Organization Methodology

The MyStocks project follows a strict file organization methodology to maintain a clean, navigable codebase. This methodology supports both **pre-classification** (proactive) and **post-classification** (reactive) approaches.

### Root Directory Policy

**ONLY these 5 core files belong in root**:
- `README.md`
- `CLAUDE.md`
- `CHANGELOG.md`
- `requirements.txt`
- `.mcp.json`

**ALL other files MUST be organized into subdirectories**.

### Directory Structure Rules

#### 1. scripts/ - Executable Scripts

**scripts/tests/** - Test Files
- **Pattern**: Files prefixed with `test_`
- **Purpose**: Unit tests, integration tests, acceptance tests
- **Examples**: `test_config_driven_table_manager.py`, `test_financial_adapter.py`

**scripts/runtime/** - Production Scripts
- **Pattern**: Files prefixed with `run_`, `save_`, `monitor_`, or `*_demo.py`
- **Purpose**: Production data collection, monitoring, demonstrations
- **Examples**: `run_realtime_market_saver.py`, `system_demo.py`

**scripts/database/** - Database Operations
- **Pattern**: Files prefixed with `check_`, `verify_`, `create_`
- **Purpose**: Database initialization, validation, management
- **Examples**: `check_tdengine_tables.py`, `verify_tdengine_deployment.py`

**scripts/dev/** - Development Tools
- **Pattern**: Development utilities not fitting other categories
- **Purpose**: Code validation, testing utilities, development aids
- **Examples**: `gpu_test_examples.py`, `validate_documentation_consistency.py`

#### 2. docs/ - Documentation Files

**docs/guides/** - User and Developer Guides
- Getting started guides, workflow documentation
- Examples: `QUICKSTART.md`, `IFLOW.md`

**docs/archived/** - Deprecated Documentation
- Preserved for historical reference
- Rule: Add deprecation notice at top when archiving

**docs/architecture/** - Architecture Design
- System design, technical architecture documentation

**docs/api/** - API Documentation
- API reference, endpoint documentation, SDK guides

#### 3. config/ - Configuration Files

All configuration files regardless of extension:
- `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- Examples: Table configs, Docker setups, test configs, build configs

#### 4. reports/ - Generated Reports

Analysis scripts output, timestamped if recurring:
- Extensions: `.json`, `.txt`, analysis outputs
- Naming: Use ISO date format `YYYYMMDD_HHMMSS` for timestamped files

### Pre-Classification (Proactive)

**When creating new files**, place them directly in the correct location:

1. **Determine file purpose**: Test? Runtime? Configuration? Documentation?
2. **Match against rules**: Use the directory structure above
3. **Create in correct location**: Never create in root unless it's one of the 5 core files

**Example**:
```python
# ✅ CORRECT: Create directly in scripts/tests/
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)

# ❌ INCORRECT: Creating in root
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

### Post-Classification (Reactive)

**When organizing existing files**:

1. **Identify misplaced files**: Use `ls` or `find` to list root directory files
2. **Categorize by rules**: Match each file against the directory structure rules
3. **Plan the reorganization**: Create a categorization plan before execution
4. **Use git mv**: Preserve file history when moving tracked files
5. **Update references**: Update all import paths, documentation links
6. **Validate**: Test that moved files work correctly

**Workflow**:
```bash
# 1. List root directory files (exclude core 5)
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. For each file, determine correct location using rules

# 3. Move files (use git mv for tracked files)
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. Update references in affected files

# 5. Commit with descriptive message
git commit -m "refactor: organize files according to directory structure rules"
```

### Import Path Management

**Critical Rule**: All scripts in `scripts/**/` must calculate project root correctly.

**Standard Pattern**:
```python
import sys
import os
from pathlib import Path

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now you can import from project root
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
```

### Git Best Practices

**Always use `git mv` for tracked files**:
```bash
# ✅ CORRECT: Preserves file history
git mv old_location/file.py new_location/file.py

# ❌ INCORRECT: Breaks file history
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

### Validation Checklist

After any file reorganization:

- [ ] Root directory contains only the 5 core files
- [ ] All scripts properly categorized in scripts/{tests,runtime,database,dev}
- [ ] All documentation in docs/{guides,archived,architecture,api}
- [ ] All configuration files in config/
- [ ] All reports in reports/
- [ ] All moved scripts have updated import paths (3-level dirname)
- [ ] All documentation links updated to new paths
- [ ] `git status` shows moves (not deletions + additions)
- [ ] All tests pass after reorganization
- [ ] `scripts/README.md` is up to date

### Common Mistakes to Avoid

1. **Creating files in root**: Always use subdirectories unless it's one of the 5 core files
2. **Wrong import paths**: Remember to use 3-level dirname for scripts in nested directories
3. **Using `mv` instead of `git mv`**: Always preserve git history
4. **Forgetting to update references**: Check all imports, documentation links
5. **Mixing purposes**: Don't put test files in runtime/, or config files in docs/

---

## 📊 Project Metrics

### Documentation Organization (2025-11-08 Cleanup)

**Before Cleanup**:
- Root directory: 55+ files
- Python scripts: 29 files in root
- Documentation files: 26 files in root

**After Cleanup**:
- Root directory: 10 files (5 core + 5 directories)
- Python scripts: 5 core modules in root, 24 organized in scripts/
- Documentation files: 5 core in root, 14 organized in docs/

**Improvement**: 81.8% reduction in root directory clutter

### Directory Breakdown

```
/opt/claude/mystocks_spec/
├── README.md, CLAUDE.md, CHANGELOG.md, requirements.txt, .mcp.json (5 core files)
├── scripts/
│   ├── tests/ (15 test files)
│   ├── runtime/ (4 production scripts)
│   ├── database/ (3 database operations)
│   └── dev/ (2 development utilities)
├── docs/
│   ├── guides/ (2 active guides)
│   ├── archived/ (2 deprecated docs)
│   ├── architecture/ (future)
│   └── api/ (future)
├── config/ (4 configuration files)
└── reports/ (4 analysis reports)
```

---

## 🔍 Finding What You Need

### By Task Type

**I want to...**

- **Learn about the project**: → [README.md](./README.md)
- **Get started quickly**: → [docs/guides/QUICKSTART.md](./docs/guides/QUICKSTART.md)
- **Integrate with Claude Code**: → [CLAUDE.md](./CLAUDE.md)
- **Run tests**: → [scripts/tests/](./scripts/tests/)
- **Start the system**: → [scripts/runtime/](./scripts/runtime/)
- **Configure databases**: → [config/mystocks_table_config.yaml](./config/mystocks_table_config.yaml)
- **View system architecture**: → [README.md § Architecture](./README.md#high-level-architecture)
- **Check recent changes**: → [CHANGELOG.md](./CHANGELOG.md)
- **Understand file organization**: → This document

### By File Type

**Looking for...**

- **Python scripts**: → [scripts/](./scripts/) (organized by function)
- **Configuration files**: → [config/](./config/)
- **Documentation**: → [docs/](./docs/) or root-level .md files
- **Test files**: → [scripts/tests/](./scripts/tests/)
- **Reports**: → [reports/](./reports/)

### Search Commands

```bash
# Find all markdown files
find . -name "*.md" -type f

# Search for specific topic in docs
grep -r "TDengine" docs/

# List configuration files
ls -lh config/

# Find Python scripts
find scripts -name "*.py" -type f

# Search in all files
grep -r "search_term" .
```

---

## 📝 Documentation Standards

### For New Documentation

When creating new documentation:

1. **Choose the right location**:
   - User guides → `docs/guides/`
   - Architecture docs → `docs/architecture/`
   - API docs → `docs/api/`
   - Core project info → Root level (rare)

2. **Use clear titles**: Start with `# Title` (H1)

3. **Add metadata**:
   ```markdown
   **Last Updated**: YYYY-MM-DD
   **Version**: X.Y
   **Audience**: [Developers/Users/All]
   ```

4. **Include examples**: Code examples should be tested

5. **Link appropriately**: Use relative links, check they work

### Quality Checklist

For each new documentation file:

- [ ] Clear title and purpose
- [ ] Target audience specified
- [ ] Last updated date
- [ ] Code examples tested
- [ ] Links verified
- [ ] Proper markdown formatting
- [ ] Added to this navigation guide (if major)

---

## 🔄 Maintenance

### Regular Tasks

**Weekly**:
- Review new files in root directory
- Ensure proper categorization
- Update links if files moved

**Monthly**:
- Review and update CHANGELOG.md
- Archive deprecated documentation
- Update documentation metrics

**Quarterly**:
- Full documentation audit
- Update this navigation guide
- Clean up outdated reports

### When to Archive Documentation

Move documentation to `docs/archived/` when:

1. Replaced by newer documentation
2. Feature/module has been removed
3. No longer reflects current architecture
4. Still valuable for historical context

**Process**:
1. Add deprecation notice at top:
   ```markdown
   > **⚠️ DEPRECATED**: This document has been replaced by [new_doc.md](link).
   > Kept for historical reference only.
   ```
2. Move to `docs/archived/`
3. Update all references to point to new documentation
4. Add entry to CHANGELOG.md

---

## 🆘 Getting Help

### Documentation Issues

If you find:
- **Broken links**: Check [docs/DOCUMENTATION_STRUCTURE.md](./docs/DOCUMENTATION_STRUCTURE.md) for current locations
- **Outdated information**: Check [CHANGELOG.md](./CHANGELOG.md) for recent changes
- **Missing documentation**: Refer to [README.md](./README.md) or [CLAUDE.md](./CLAUDE.md)

### File Organization Questions

For file organization guidance:
- Review this guide's [File Organization Methodology](#file-organization-methodology)
- Check [CLAUDE.md § File Organization Rules](./CLAUDE.md#file-organization-rules)
- See [.specify/memory/constitution.md § 文件组织规范](./.specify/memory/constitution.md)

---

## 📚 Related Resources

### Internal Documentation

- **[README.md](./README.md)** - Main project documentation
- **[CLAUDE.md](./CLAUDE.md)** - AI development guide with file organization rules
- **[scripts/README.md](./scripts/README.md)** - Script organization detailed guide
- **[docs/DOCUMENTATION_STRUCTURE.md](./docs/DOCUMENTATION_STRUCTURE.md)** - Complete file inventory
- **[.specify/memory/constitution.md](./.specify/memory/constitution.md)** - Project constitution (includes file organization in Chinese)
- **[.taskmaster/CLAUDE.md](./.taskmaster/CLAUDE.md)** - TaskMaster integration guide

### External Resources

- **[Claude Code Documentation](https://docs.claude.com/claude-code)** - Official Claude Code docs
- **[TaskMaster Documentation](https://task-master.ai)** - TaskMaster workflow tool
- **[TDengine Documentation](https://docs.tdengine.com)** - Time-series database
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/)** - Relational database
- **[TimescaleDB Documentation](https://docs.timescale.com)** - PostgreSQL extension

---

**Last Updated**: 2025-11-08
**Maintained by**: MyStocks Development Team
**Version**: 1.0

For questions or suggestions, refer to project maintainers or submit an issue.
