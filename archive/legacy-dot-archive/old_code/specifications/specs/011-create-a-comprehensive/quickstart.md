# Quickstart Guide: MyStocks Function Classification Manual

**Purpose**: Help developers quickly understand and use the Function Classification Manual
**Audience**: Developers, architects, and technical leads working on MyStocks
**Last Updated**: 2025-10-19

## Table of Contents

1. [What is the Classification Manual?](#what-is-the-classification-manual)
2. [Navigating the Manual](#navigating-the-manual)
3. [Understanding Categories](#understanding-categories)
4. [Using the Manual for Common Tasks](#using-the-manual-for-common-tasks)
5. [Updating the Manual](#updating-the-manual)
6. [Interpreting Duplication Reports](#interpreting-duplication-reports)
7. [Following Optimization Recommendations](#following-optimization-recommendations)

---

## What is the Classification Manual?

The **MyStocks Function Classification Manual** is a comprehensive documentation system that:

- **Categorizes all 160+ Python modules** into 5 logical categories
- **Documents every class and function** with purpose, parameters, and relationships
- **Identifies code duplications** with consolidation recommendations
- **Maps data flows** through the entire system
- **Provides optimization roadmap** with prioritized improvements

### Who Should Use It?

| Role | Primary Use Cases |
|------|------------------|
| **New Developers** | Understand system architecture, locate functionality quickly |
| **Senior Developers** | Review consolidation opportunities, plan refactoring |
| **Architects** | Assess system design, identify architecture issues |
| **Technical Leads** | Plan optimization work, allocate resources |
| **Code Reviewers** | Verify changes align with system patterns |

### Key Benefits

✅ **Faster Onboarding**: New developers locate functionality in 10 minutes vs. hours of code exploration
✅ **Reduced Duplication**: Identify and consolidate duplicate code, reducing maintenance burden
✅ **Better Decisions**: Make informed refactoring decisions based on complete system understanding
✅ **Improved Quality**: Follow established patterns, avoid reinventing the wheel

---

## Navigating the Manual

### Directory Structure

```
docs/function-classification-manual/
├── README.md                      # 👈 Start here! Overview and navigation
│
├── 01-core-functions.md           # Entry points, orchestration (unified_manager, core)
├── 02-auxiliary-functions.md      # Data adapters, strategies (adapters/, strategy/)
├── 03-infrastructure-functions.md # Database, config (db_manager/, config/)
├── 04-monitoring-functions.md     # Observability (monitoring/)
├── 05-utility-functions.md        # Helpers (utils/)
│
├── 06-duplication-analysis.md     # 🔥 Code duplications & consolidation
├── 07-optimization-roadmap.md     # 🚀 Prioritized improvements
├── 08-consolidation-guide.md      # 📋 Step-by-step merge guides
├── 09-data-flow-maps.md           # 📊 Architecture diagrams
│
└── metadata/                      # Machine-readable data
    ├── module-inventory.json      # All modules indexed
    ├── duplication-index.json     # Duplication cases
    └── dependency-graph.json      # Import relationships
```

### How to Find Specific Modules

#### Method 1: Search by Filename

Use your editor's file search (`Ctrl+P` in VSCode):
```
# Find where "akshare" is documented
Search: "akshare" in docs/function-classification-manual/

# Result: 02-auxiliary-functions.md, section "adapters/akshare_adapter.py"
```

#### Method 2: Search by Functionality

Use text search (`Ctrl+Shift+F` in VSCode):
```
# Find modules related to "monitoring"
Search: "monitoring" in docs/function-classification-manual/*.md

# Results:
# - 04-monitoring-functions.md: MonitoringDatabase, PerformanceMonitor
# - 01-core-functions.md: unified_manager (uses monitoring)
```

#### Method 3: Browse by Category

Open the appropriate category file:
- Need to modify data access? → `01-core-functions.md` → Look for `data_access/`
- Adding a new adapter? → `02-auxiliary-functions.md` → Review existing adapters
- Database connection issue? → `03-infrastructure-functions.md` → Check `db_manager/`

#### Method 4: Query JSON Metadata

Use `jq` to query module inventory:
```bash
# Find all modules in 'core' category
jq '.modules[] | select(.category == "core") | .module_name' metadata/module-inventory.json

# Find modules with > 500 LOC
jq '.modules[] | select(.lines_of_code > 500) | {name: .module_name, loc: .lines_of_code}' metadata/module-inventory.json

# Find all modules that import 'monitoring'
jq '.modules[] | select(.imports[] | contains("monitoring")) | .module_name' metadata/module-inventory.json
```

---

## Understanding Categories

The manual organizes code into **5 primary categories** based on purpose and responsibility:

### 1. Core Functions (核心功能)

**Purpose**: Entry points, orchestration, critical business logic

**Key Modules**:
- `unified_manager.py` - Central data operations manager
- `core.py` - Data classification and routing
- `data_access.py` - Unified data access layer
- `monitoring.py` - System monitoring integration

**When to Look Here**:
- Understanding main system flow
- Modifying data routing logic
- Changing data classification rules
- Integrating new databases

**Example**: *"I need to add support for a new data classification. Where do I start?"*
→ `01-core-functions.md` → `core.py` → `DataClassification` enum

---

### 2. Auxiliary Functions (辅助功能)

**Purpose**: Data source adapters, strategies, backtesting

**Key Modules**:
- `adapters/akshare_adapter.py` - Akshare data source
- `adapters/tdx_adapter.py` - TDX binary data import
- `strategy/base_strategy.py` - Trading strategy framework
- `backtest/backtest_engine.py` - Backtesting engine

**When to Look Here**:
- Adding new data source
- Creating new trading strategy
- Modifying data adapters
- Understanding data source patterns

**Example**: *"I want to add support for a new data provider API"*
→ `02-auxiliary-functions.md` → Review existing adapters → Implement `IDataSource` interface

---

### 3. Infrastructure Functions (基础设施)

**Purpose**: Database management, configuration, ORM models

**Key Modules**:
- `db_manager/database_manager.py` - Multi-database connection manager
- `db_manager/connection_manager.py` - Connection pooling
- `core/config_driven_table_manager.py` - YAML-driven table creation

**When to Look Here**:
- Database connection issues
- Adding new table configurations
- Modifying database schemas
- Understanding connection lifecycle

**Example**: *"Database connections are timing out. Where is connection management?"*
→ `03-infrastructure-functions.md` → `db_manager/connection_manager.py`

---

### 4. Monitoring Functions (监控功能)

**Purpose**: Observability, performance tracking, alerts

**Key Modules**:
- `monitoring/monitoring_database.py` - Operation logging
- `monitoring/performance_monitor.py` - Query performance tracking
- `monitoring/data_quality_monitor.py` - Data quality checks
- `monitoring/alert_manager.py` - Alert dispatch

**When to Look Here**:
- Adding new metrics
- Investigating performance issues
- Setting up alerts
- Reviewing operation logs

**Example**: *"I need to track performance of a new operation"*
→ `04-monitoring-functions.md` → `PerformanceMonitor` → Use `@track_operation` decorator

---

### 5. Utility Functions (工具功能)

**Purpose**: Helper functions, decorators, validation scripts

**Key Modules**:
- `utils/date_utils.py` - Date handling and normalization
- `utils/symbol_utils.py` - Stock symbol formatting
- `utils/column_mapper.py` - Column name mapping
- `utils/failure_recovery_queue.py` - Retry logic

**When to Look Here**:
- Need common helper function
- Adding validation logic
- Creating reusable decorator
- Finding existing utilities

**Example**: *"I need to normalize a date string. Is there a utility for this?"*
→ `05-utility-functions.md` → `utils/date_utils.py` → `normalize_date()` function

---

## Using the Manual for Common Tasks

### Task 1: Adding a New Feature

**Scenario**: You need to add support for intraday 5-minute bar data.

**Steps**:

1. **Understand data flow**:
   - Read `09-data-flow-maps.md` → End-to-end flow diagram
   - Identify: External source → Adapter → Unified Manager → Database

2. **Check if classification exists**:
   - Read `01-core-functions.md` → `core.py` → `DataClassification`
   - See `MINUTE_KLINE` already exists for minute data

3. **Find similar implementation**:
   - Search manual for "MINUTE_KLINE"
   - Find existing handling in `unified_manager.py`

4. **Identify required changes**:
   - Add data source adapter (if needed) → Review `02-auxiliary-functions.md`
   - Ensure routing to TDengine → Check `core.py` routing rules
   - Add table config → See `table_config.yaml` examples

### Task 2: Finding Where to Add Code

**Scenario**: You need to add a new indicator calculation.

**Decision Tree**:

```
Is it a data source adapter?
    → YES: Add to adapters/, review 02-auxiliary-functions.md

Is it core orchestration/routing?
    → YES: Add to core modules, review 01-core-functions.md

Is it monitoring/metrics?
    → YES: Add to monitoring/, review 04-monitoring-functions.md

Is it a helper function?
    → YES: Add to utils/, review 05-utility-functions.md

Is it a trading strategy?
    → YES: Add to strategy/, review 02-auxiliary-functions.md (strategies section)

Is it a database operation?
    → YES: Add to db_manager/ or data_access/, review 01-core-functions.md or 03-infrastructure-functions.md
```

### Task 3: Understanding Module Dependencies

**Scenario**: You want to understand what depends on `monitoring.py`.

**Options**:

**Option A: Read the manual**
- Open `04-monitoring-functions.md` → `monitoring.py` section
- Look for "Used By" section → Lists all dependent modules

**Option B: Query metadata**
```bash
# Find all modules that depend on monitoring
jq '.modules[] | select(.depends_on[] | contains("monitoring")) | .module_name' metadata/module-inventory.json
```

**Option C: View dependency graph**
- Open `09-data-flow-maps.md` → Dependency graph diagrams
- Locate `monitoring` node → Follow incoming edges

### Task 4: Refactoring Safely

**Scenario**: You want to refactor `data_access.py`.

**Steps**:

1. **Understand current structure**:
   - Read `01-core-functions.md` → `data_access.py` section
   - Review all classes, methods, and their purposes

2. **Identify dependencies**:
   - Check "Used By" section in manual
   - Query `dependency-graph.json` for reverse dependencies

3. **Review consolidation opportunities**:
   - Read `06-duplication-analysis.md` → Search for "data_access"
   - See if there are duplicate patterns to consolidate

4. **Check optimization recommendations**:
   - Read `07-optimization-roadmap.md` → Search for "data_access"
   - Review any existing optimization suggestions

5. **Plan changes**:
   - Review `08-consolidation-guide.md` for merge patterns
   - Follow testing strategy recommendations

---

## Updating the Manual

### When to Update

Update the manual after:

✅ **Major code changes** (> 10 files modified OR > 5000 LOC changed)
✅ **New module categories** (adding new directories)
✅ **Architecture changes** (new patterns, refactoring)
✅ **Quarterly reviews** (keep manual fresh)

❌ **Don't update for**:
- Minor bug fixes (< 5 files)
- Documentation-only changes
- Test updates

### How to Regenerate

**Full Regeneration** (all sections):

```bash
cd /opt/claude/mystocks_spec

# Run analysis and generate manual
python scripts/analysis/generate_manual.py --full

# Review changes
git diff docs/function-classification-manual/

# Commit if satisfied
git add docs/function-classification-manual/
git commit -m "Update function classification manual - $(date +%Y-%m-%d)"
```

**Partial Update** (specific sections):

```bash
# Update only duplication analysis
python scripts/analysis/generate_manual.py --section duplication_analysis

# Update only core functions documentation
python scripts/analysis/generate_manual.py --section core_functions

# Update metadata only
python scripts/analysis/generate_manual.py --metadata-only
```

**Using the Update Script** (after implementation):

```bash
# Use provided update script
cd docs/function-classification-manual/templates
./update-manual.sh --help

# Run with default settings
./update-manual.sh

# Run with specific sections
./update-manual.sh --sections="duplication_analysis,optimization_roadmap"
```

### Validation After Update

Always validate after regeneration:

```bash
# Check all required files exist
ls -la docs/function-classification-manual/*.md

# Validate JSON metadata
jq empty metadata/*.json  # Should output nothing if valid

# Check for broken links
grep -r "\[.*\](.*)" docs/function-classification-manual/*.md | grep "404"

# Verify module count matches
jq '.modules | length' metadata/module-inventory.json
# Should match: find . -name "*.py" | wc -l
```

---

## Interpreting Duplication Reports

### Severity Levels

The duplication analysis uses 4 severity levels:

| Severity | Token Similarity | AST Similarity | Interpretation | Action |
|----------|-----------------|----------------|----------------|--------|
| **CRITICAL** 🔴 | ≥ 95% | ≥ 90% | Nearly identical code | **Fix immediately** |
| **HIGH** 🟠 | 80-94% | 70-89% | Significant duplication | **Fix soon** (next sprint) |
| **MEDIUM** 🟡 | 60-79% | 50-69% | Similar patterns | **Consider refactoring** |
| **LOW** 🟢 | 40-59% | 30-49% | Coincidental similarity | **Review only** |

### Reading a Duplication Report

Example from `06-duplication-analysis.md`:

```markdown
### dup_001: Retry Decorator Pattern

🔴 **CRITICAL** | Token: 92% | AST: 88% | Combined: 90%

**Locations**:

📄 `adapters/akshare_adapter.py` (lines 50-75)
```python
def _retry_api_call(self, func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

📄 `adapters/baostock_adapter.py` (lines 45-70)
```python
def _retry_api_call(self, func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

**Recommendation**:
Extract to `utils/retry_decorator.py` as `@retry_decorator(max_attempts=3)`.
Update both adapters to use decorator instead of method.

**Effort**: 1 hour
```

### Prioritizing Fixes

Use this decision matrix:

```
Priority = (Severity Weight × 10) + (Frequency Weight × 5)

Severity Weight:
- CRITICAL: 4
- HIGH: 3
- MEDIUM: 2
- LOW: 1

Frequency Weight:
- Used in 10+ locations: 4
- Used in 5-9 locations: 3
- Used in 3-4 locations: 2
- Used in 2 locations: 1

Example:
- CRITICAL duplication in 12 locations:
  Priority = (4 × 10) + (4 × 5) = 60 (highest priority)

- HIGH duplication in 2 locations:
  Priority = (3 × 10) + (1 × 5) = 35 (medium priority)
```

### Consolidation Strategies

See `08-consolidation-guide.md` for detailed strategies:

1. **Extract Base Class** - For similar classes
2. **Extract Utility Function** - For duplicate helpers
3. **Extract Decorator** - For cross-cutting concerns
4. **Consolidate Modules** - For overlapping functionality

---

## Following Optimization Recommendations

### Understanding the Roadmap

The optimization roadmap (`07-optimization-roadmap.md`) organizes improvements by:

- **Priority**: CRITICAL → HIGH → MEDIUM → LOW
- **Type**: performance, architecture, code_quality, security
- **Effort**: Quick wins (<4 hours) vs. Major refactoring (>1 week)

### Quick Wins Matrix

Start here for low-effort, high-impact improvements:

| ID | Title | Priority | Effort | Impact |
|----|-------|----------|--------|--------|
| opt_012 | Add missing indexes to MySQL tables | HIGH | 2 hours | 50ms query speedup |
| opt_018 | Fix N+1 query in dashboard | HIGH | 3 hours | 80% latency reduction |
| opt_024 | Add connection pool config | CRITICAL | 4 hours | Prevent connection exhaustion |

### Priority vs. Effort Chart

```
High Impact ▲
           │
    [3]    │  [1]     1 = CRITICAL priority, low effort (DO FIRST)
           │  [2]     2 = HIGH priority, low effort
           │          3 = HIGH priority, high effort
───────────┼──────────► High Effort
    [4]    │
           │          4 = LOW priority, low effort (nice to have)
```

### Implementation Workflow

For each optimization opportunity:

1. **Read full description** in `07-optimization-roadmap.md`
2. **Review implementation steps** (numbered list)
3. **Check affected modules** (files that need changes)
4. **Follow testing strategy** (how to verify)
5. **Keep rollback plan handy** (how to revert if issues)

**Example**:

```markdown
### opt_001: Implement connection pooling

**Current State**: Individual connections per operation. No pooling.

**Proposed Change**: Create singleton connection pools with configurable max_size.

**Expected Impact**:
- Reduce connection overhead by 70%
- Improve response time by 30-50ms
- Prevent connection exhaustion

**Implementation Steps**:
1. Create `db_manager/connection_pool.py`
2. Implement database-specific pool classes
3. Update `DatabaseTableManager` to use pools
4. Add pool configuration to .env
5. Add pool monitoring metrics

**Affected Modules**:
- db_manager/database_manager.py
- db_manager/connection_manager.py
- data_access/*.py

**Testing Strategy**:
- Load test with 100 concurrent users
- Verify connection count ≤ max_size
- Measure latency improvement

**Effort**: 8-12 hours
```

---

## Tips for Best Results

### ✅ Do's

✅ **Always read README.md first** for overview and navigation
✅ **Use search** to find modules quickly
✅ **Check duplication report** before adding new code
✅ **Review optimization roadmap** quarterly
✅ **Update manual** after major changes
✅ **Query JSON metadata** for complex queries

### ❌ Don'ts

❌ **Don't skip the manual** and dive straight into code
❌ **Don't add duplicate code** without checking duplication report
❌ **Don't ignore CRITICAL optimizations** - they block production
❌ **Don't let manual get stale** - update after major changes
❌ **Don't modify generated files manually** - regenerate instead

---

## Getting Help

### Common Issues

**"I can't find a specific module in the manual"**
→ Use file search (`Ctrl+P`) or text search (`Ctrl+Shift+F`)
→ Try searching in `metadata/module-inventory.json`

**"The manual is outdated"**
→ Run `./templates/update-manual.sh` to regenerate
→ Check `git log docs/function-classification-manual/` to see last update

**"I don't understand a duplication report"**
→ Read the "Interpreting Duplication Reports" section above
→ Look for similar examples in `06-duplication-analysis.md`

**"Where should I add my new code?"**
→ Use the decision tree in "Task 2: Finding Where to Add Code"
→ Look for similar functionality in the appropriate category file

### Additional Resources

- **Project Constitution**: `.specify/memory/constitution.md` - Core architectural principles
- **Development Guide**: `CLAUDE.md` - Development commands and workflows
- **Architecture Docs**: `docs/architecture/` - Detailed architecture documentation

---

**Last Updated**: 2025-10-19
**Manual Version**: 1.0.0
**Questions?** Open an issue or ask in the team chat!
