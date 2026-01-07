# 📚 MyStocks Documentation Structure

**Last Updated**: 2025-11-08
**Version**: 1.0

## 📁 Documentation Organization

This document describes the organized documentation structure of the MyStocks project after the 2025-11-08 cleanup.

---

## 🌳 Directory Structure

```
/opt/claude/mystocks_spec/
├── README.md                      # Main project documentation
├── CLAUDE.md                      # Claude Code integration guide
├── CHANGELOG.md                   # Version history and changes
├── requirements.txt               # Python dependencies
├── .mcp.json                      # MCP server configuration
│
├── docs/
│   ├── guides/                    # User and developer guides
│   │   ├── QUICKSTART.md          # Quick start guide
│   │   └── IFLOW.md               # Workflow documentation
│   │
│   ├── archived/                  # Archived/deprecated documentation
│   │   ├── START_HERE.md          # Old entry point (deprecated)
│   │   └── TASKMASTER_START_HERE.md  # Old TaskMaster guide (use .taskmaster/CLAUDE.md)
│   │
│   ├── architecture/              # Architecture design docs
│   └── api/                       # API documentation
│
├── config/
│   ├── mystocks_table_config.yaml     # Main table configuration
│   ├── docker-compose.tdengine.yml    # TDengine Docker setup
│   ├── .readthedocs.yaml              # ReadTheDocs configuration
│   └── pytest.ini                     # Pytest configuration
│
├── reports/                       # Analysis reports and assessments
│   ├── database_assessment_20251019_165817.json
│   ├── dump_result.txt
│   ├── query_patterns_analysis.txt
│   └── WENCAI_INTEGRATION_FILES.txt
│
└── scripts/
    ├── tests/
    │   ├── test_requirements.txt   # Test dependencies
    │   └── coverage.xml           # Test coverage report
    │
    └── dev/
        └── git_commit_comments.txt  # Commit message templates
```

---

## 📖 Core Documentation

### Root Level (Must-Read)

| File | Purpose | Target Audience |
|------|---------|-----------------|
| `README.md` | Project overview, features, architecture | All users |
| `CLAUDE.md` | Claude Code integration and commands | Developers using Claude |
| `CHANGELOG.md` | Version history and updates | All users |
| `requirements.txt` | Python package dependencies | Developers, DevOps |
| `.mcp.json` | MCP server configuration | Claude Code users |

---

## 📚 Documentation Categories

### 1. Guides (`docs/guides/`)

**User and Developer Guides**

- **QUICKSTART.md** (13K)
  Quick start guide for new users, setup instructions, basic usage

- **IFLOW.md** (12K)
  Project workflow documentation, development processes

**Usage**:
```bash
# Read quick start guide
cat docs/guides/QUICKSTART.md

# Follow workflow guide
cat docs/guides/IFLOW.md
```

---

### 2. Archived Documentation (`docs/archived/`)

**Deprecated but Preserved for Reference**

- **START_HERE.md** (9.2K)
  Old entry point document, replaced by README.md and docs/guides/QUICKSTART.md

- **TASKMASTER_START_HERE.md** (7.2K)
  Old TaskMaster documentation, replaced by `.taskmaster/CLAUDE.md`

**Note**: These files are kept for historical reference but should not be used for current development.

---

### 3. Configuration Files (`config/`)

**System Configuration**

| File | Purpose | Used By |
|------|---------|---------|
| `mystocks_table_config.yaml` (38K) | Main database table definitions | ConfigDrivenTableManager |
| `docker-compose.tdengine.yml` (1.9K) | TDengine Docker Compose setup | Docker deployment |
| `.readthedocs.yaml` (600B) | ReadTheDocs build configuration | Documentation hosting |
| `pytest.ini` (1.2K) | Pytest configuration and settings | Test framework |

**Usage**:
```bash
# View table configuration
cat config/mystocks_table_config.yaml

# Start TDengine with Docker
docker-compose -f config/docker-compose.tdengine.yml up -d

# Run tests with pytest config
pytest -c config/pytest.ini
```

---

### 4. Reports & Analysis (`reports/`)

**Generated Reports and Analysis Files**

- **database_assessment_20251019_165817.json** (841B)
  Database architecture assessment from Week 3 simplification

- **dump_result.txt** (2.0K)
  TDengine backup/dump operation logs

- **query_patterns_analysis.txt** (3.2K)
  Query pattern analysis for optimization

- **WENCAI_INTEGRATION_FILES.txt** (8.3K)
  Wencai (问财) integration file inventory

---

### 5. Test Documentation (`scripts/tests/`)

- **test_requirements.txt** (650B)
  Testing-specific Python dependencies

- **coverage.xml** (251K)
  Test coverage report in XML format

---

## 🗑️ Removed Files

The following files were removed during the 2025-11-08 cleanup:

| File | Reason | Action |
|------|--------|--------|
| `cookie.txt` | Empty cookie file | Deleted |
| `mystocks_system.log` | Empty log file | Deleted |
| `realtime_data_save.log` | Empty log file | Deleted |
| `realtime_market_saver.log` | Runtime log (should be in logs/) | Deleted |
| `financial_adapter.log` | Runtime log (should be in logs/) | Deleted |
| `table_config.yaml` | Replaced by `mystocks_table_config.yaml` | Deleted |
| `package-lock.json` | Invalid (no NPM dependencies) | Deleted |

---

## 📊 Documentation Metrics

### Before Cleanup (2025-11-08)
- **Total files in root**: 26 documentation files
- **Core documentation**: 5 files
- **Scattered files**: 21 files

### After Cleanup (2025-11-08)
- **Total files in root**: 5 files
- **Organized in subdirectories**: 14 files
- **Deleted obsolete**: 7 files

**Improvement**: **80.8%** reduction in root directory clutter 🎉

---

## 🔍 Finding Documentation

### Quick Reference

```bash
# Project overview
cat README.md

# Quick start
cat docs/guides/QUICKSTART.md

# Claude Code integration
cat CLAUDE.md

# Configuration reference
cat config/mystocks_table_config.yaml

# Recent changes
cat CHANGELOG.md
```

### Search Documentation

```bash
# Find all markdown files
find docs -name "*.md"

# Search for specific topic
grep -r "TDengine" docs/

# List configuration files
ls -lh config/
```

---

## 🔗 Related Resources

- **Architecture Documentation**: `docs/architecture/`
- **API Documentation**: `docs/api/`
- **Script Documentation**: `scripts/README.md`
- **TaskMaster Integration**: `.taskmaster/CLAUDE.md`

---

## 📝 Maintenance Guidelines

### Adding New Documentation

1. **User Guides**: Add to `docs/guides/`
2. **Architecture Docs**: Add to `docs/architecture/`
3. **API Docs**: Add to `docs/api/`
4. **Reports**: Add to `reports/` with timestamp suffix

### Deprecating Documentation

1. Move to `docs/archived/`
2. Add deprecation note at top of file
3. Update references in other documents
4. Document in CHANGELOG.md

### Configuration Changes

1. Update files in `config/`
2. Test configuration changes
3. Document breaking changes in CHANGELOG.md
4. Update related documentation

---

## ✅ Quality Checklist

For each new documentation file:

- [ ] Clear title and purpose
- [ ] Target audience specified
- [ ] Last updated date
- [ ] Code examples tested
- [ ] Links verified
- [ ] Proper markdown formatting
- [ ] Added to this structure document

---

**Maintained by**: MyStocks Development Team
**Questions?**: Refer to README.md or CLAUDE.md for contact information
