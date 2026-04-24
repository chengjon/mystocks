# Scripts Directory

> **参考指南说明**:
> 本文件用于说明脚本目录的使用方法、目录用途、测试流程、部署步骤或辅助操作参考，帮助理解脚本层面的局部实践。
> 其中的命令、路径、步骤与示例应先与 `architecture/STANDARDS.md`、当前脚本实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独充当共享规则或当前状态的唯一事实来源。


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

# Audit OpenAPI success-response examples
python scripts/dev/openapi_success_example_audit.py --show-non-json

# Collect current technical-debt metrics
python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output /tmp/tech-debt-current.json

# Evaluate current metrics against the frozen baseline
python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate \
  --baseline reports/analysis/tech-debt-baseline.json \
  --current /tmp/tech-debt-current.json \
  --output /tmp/tech-debt-kpi-gate.json

# Generate the weekly governance report
python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report \
  --baseline reports/analysis/tech-debt-baseline.json \
  --current /tmp/tech-debt-current.json \
  --output /tmp/tech-debt-weekly-report.md

# Generate the weekly governance report via the stable local wrapper
bash scripts/run_tech_debt_weekly_report.sh

# Rebuild the combined runtime delivery summary, drift gate, and bundle locally
bash scripts/run_runtime_delivery_summary_local.sh

# Run the containerized runtime smoke on backup host ports only
POSTGRES_PASSWORD=postgres TDENGINE_PASSWORD=taosdata bash scripts/run_containerized_runtime_smoke.sh

# Run the full runtime delivery gate: docker smoke + combined summary + drift
bash scripts/run_full_runtime_delivery_gate.sh

# Audit direct view-level apiClient imports and swallowed empty catches
python scripts/compliance/frontend_data_access_report.py --strict

# Review a baseline update that needs an approved rebaseline exception
python scripts/dev/quality_gate/tech_debt_governance_gate.py baseline-review \
  --previous /tmp/tech-debt-baseline.previous.json \
  --proposed reports/analysis/tech-debt-baseline.json \
  --exceptions reports/compliance/exceptions/tech_debt_baseline_rebaseline.json

# Compare frozen baseline with current measured metrics
python scripts/dev/quality_gate/tech_debt_governance_gate.py baseline-drift-report \
  --baseline reports/analysis/tech-debt-baseline.json \
  --current /tmp/tech-debt-current.json \
  --output reports/analysis/tech-debt-baseline-drift-report.json \
  --only-drifted

# For ad hoc local inspection, you can also write to a temp file:
# --output /tmp/tech-debt-baseline-drift.json
```

---

## Import Path Note

## Runtime Delivery Entry Points

Phase 5+ containerized deployment capability uses two explicit entrypoints and keeps PM2 canonical ports separate from container smoke ports:

- Containerized runtime smoke: `POSTGRES_PASSWORD=postgres TDENGINE_PASSWORD=taosdata bash scripts/run_containerized_runtime_smoke.sh`
- Full runtime delivery gate: `bash scripts/run_full_runtime_delivery_gate.sh`
- Canonical PM2 runtime URLs: `http://localhost:8020` and `http://localhost:3020`
- Backup smoke URLs for container-only verification: `http://localhost:8021` and `http://localhost:3021`

Use the smoke entrypoint to validate compose build, readiness, and metrics collection on isolated ports. Use the full runtime delivery gate to consume that smoke evidence together with PM2/runtime drift artifacts without creating a parallel deployment truth source.

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
