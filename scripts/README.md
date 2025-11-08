# Scripts Directory

This directory contains all executable scripts organized by functionality.

## Directory Structure

### 📁 `tests/` - Test Scripts
All test scripts for validating system functionality.

```bash
scripts/tests/
├── test_config_driven_table_manager.py  # Config-driven table manager tests
├── test_customer_realtime_data.py       # Customer realtime data tests
├── test_dual_database_architecture.py   # Dual database architecture tests
├── test_financial_adapter.py            # Financial adapter tests
├── test_gpu_environment.py              # GPU environment validation
├── test_import.py                       # Import tests
├── test_ml_demo.py                      # Machine learning demo tests
├── test_save_realtime_data.py           # Realtime data saving tests
├── test_tdx_api.py                      # TDX API tests
├── test_tdx_multiperiod.py              # TDX multi-period tests
├── test_tdx_mvp.py                      # TDX MVP tests
├── test_tdx_path_validation.py          # TDX path validation tests
├── test_ths_industry.py                 # THS industry data tests
└── test_us2_acceptance.py               # US2 acceptance tests
```

**Usage:**
```bash
# Run specific test
python scripts/tests/test_config_driven_table_manager.py

# Run all tests (if test runner available)
pytest scripts/tests/
```

---

### 📁 `runtime/` - Runtime Scripts
Production runtime scripts and data collection tools.

```bash
scripts/runtime/
├── run_realtime_market_saver.py   # Main realtime market data collector
├── save_realtime_data.py          # Realtime data saving module
├── monitor_cache_stats.py         # Cache statistics monitor
└── system_demo.py                 # System demonstration script
```

**Usage:**
```bash
# Start realtime market data collection
python scripts/runtime/run_realtime_market_saver.py

# Run system demonstration
python scripts/runtime/system_demo.py

# Monitor cache statistics
python scripts/runtime/monitor_cache_stats.py
```

---

### 📁 `database/` - Database Operations
Database management, validation, and deployment scripts.

```bash
scripts/database/
├── check_tdengine_tables.py           # TDengine table validation
├── create_realtime_quotes_table.py    # Create realtime quotes table
└── verify_tdengine_deployment.py      # TDengine deployment verification
```

**Usage:**
```bash
# Check TDengine tables
python scripts/database/check_tdengine_tables.py

# Verify TDengine deployment
python scripts/database/verify_tdengine_deployment.py

# Create realtime quotes table
python scripts/database/create_realtime_quotes_table.py
```

---

### 📁 `dev/` - Development Tools
Development utilities and validation tools.

```bash
scripts/dev/
├── gpu_test_examples.py                    # GPU acceleration test examples
└── validate_documentation_consistency.py   # Documentation consistency validator
```

**Usage:**
```bash
# Test GPU environment
python scripts/dev/gpu_test_examples.py

# Validate documentation consistency
python scripts/dev/validate_documentation_consistency.py
```

---

## Import Path Note

All scripts have been updated to use correct import paths from the project root:

```python
# Standard pattern in all scripts
import sys
import os
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now import from project modules
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
```

---

## Root Directory Structure

After reorganization, the project root only contains core modules:

```
/opt/claude/mystocks_spec/
├── __init__.py           # Package marker
├── core.py              # Core architecture (DataClassification, StorageStrategy)
├── data_access.py       # Data access layer (TDengine/PostgreSQL)
├── unified_manager.py   # Unified manager
├── monitoring.py        # Monitoring module
├── adapters/            # Data source adapters
├── db_manager/          # Database management
└── scripts/             # All executable scripts (this directory)
```

---

## Related Documentation

- Main project documentation: `/CLAUDE.md`
- Development guidelines: `/项目开发规范与指导文档.md`
- Configuration guide: `/config/table_config.yaml`

---

**Last Updated:** 2025-11-08
**Reorganization:** Cleaned up root directory from 29 files to 5 core modules
