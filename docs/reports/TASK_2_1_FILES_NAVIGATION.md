# Task 2.1 - Files and Navigation Guide

**Task**: TDengine 缓存服务搭建 (TDengine Cache Service Setup)
**Status**: ✅ COMPLETE
**Date**: 2025-11-06

---

## 📋 Quick File Index

| File | Purpose | Lines | Priority |
|------|---------|-------|----------|
| **Core Implementation** |
| `web/backend/app/core/tdengine_manager.py` | Main manager class | 474 | 🔴 Critical |
| **Testing** |
| `web/backend/tests/test_tdengine_manager.py` | Integration tests (27 cases) | 650+ | 🔴 Critical |
| **Deployment** |
| `docker-compose.tdengine.yml` | Container configuration | 82 | 🔴 Critical |
| `verify_tdengine_deployment.py` | Deployment verification | 420+ | 🟡 Important |
| `monitor_cache_stats.py` | Real-time monitoring | 350+ | 🟡 Important |
| **Documentation** |
| `TASK_2_1_DEPLOYMENT_GUIDE.md` | Deployment instructions | 500+ | 🟡 Important |
| `TDENGINE_QUICK_REFERENCE.md` | Developer quick reference | 300+ | 🟡 Important |
| `TASK_2_1_COMPLETION_REPORT.md` | Detailed completion report | 500+ | 🟢 Reference |
| `TASK_2_IMPLEMENTATION_PLAN.md` | 4-week roadmap | 146 | 🟢 Reference |
| `SESSION_COMPLETION_2025_11_06.md` | Session summary | 400+ | 🟢 Reference |
| **Configuration** |
| `.taskmaster/tasks/tasks.json` | Task status tracking | - | 🟡 Important |

---

## 📂 File Organization by Purpose

### 🔴 Critical Files (Must Read)

#### 1. TDengineManager Implementation
**File**: `web/backend/app/core/tdengine_manager.py`
- **What**: Core TDengine connection and cache management class
- **Who should read**: All developers using cache functionality
- **When to read**: Before implementing cache operations in API endpoints
- **Key sections**:
  - Lines 25-56: Class docstring with usage examples
  - Lines 58-94: `__init__` with configuration
  - Lines 95-115: `connect()` method
  - Lines 116-142: `initialize()` method
  - Lines 202-260: `write_cache()` method
  - Lines 261-325: `read_cache()` method
  - Lines 327-354: `clear_expired_cache()` method
  - Lines 456-465: `get_tdengine_manager()` singleton factory

#### 2. Integration Tests
**File**: `web/backend/tests/test_tdengine_manager.py`
- **What**: Comprehensive test coverage (27 test cases, 100% pass rate)
- **Who should read**: QA, developers validating changes
- **When to run**: After any code changes, before deployment
- **How to run**:
  ```bash
  pytest web/backend/tests/test_tdengine_manager.py -v
  ```
- **Key test classes**:
  - `TestTDengineConnection` (Lines 25-55): Connection tests
  - `TestCacheWriteOperations` (Lines 85-155): Write functionality
  - `TestCacheReadOperations` (Lines 157-224): Read functionality
  - `TestCacheExpirationAndCleanup` (Lines 226-284): TTL and cleanup
  - `TestErrorHandling` (Lines 328-409): Error cases

#### 3. Docker Compose Configuration
**File**: `docker-compose.tdengine.yml`
- **What**: Multi-service container orchestration
- **Who should read**: DevOps, deployment engineers
- **When to use**: For deployment and local development
- **Key sections**:
  - Lines 4-47: TDengine service configuration
  - Lines 50-69: PostgreSQL service configuration
  - Lines 71-81: Volume and network definitions
- **How to deploy**:
  ```bash
  docker-compose -f docker-compose.tdengine.yml up -d
  ```

---

### 🟡 Important Files (Should Read)

#### 4. Deployment Guide
**File**: `TASK_2_1_DEPLOYMENT_GUIDE.md`
- **What**: Complete deployment and operations manual
- **Who should read**: Deployment engineers, operations team
- **When to read**: Before deploying to any environment
- **Key sections**:
  - Quick Start (lines 10-45)
  - Architecture Overview (lines 47-150)
  - Configuration Management (lines 230-265)
  - Troubleshooting (lines 267-310)
  - Next Steps (lines 312-345)
- **How to use**: Reference for deployment and troubleshooting

#### 5. Deployment Verification
**File**: `verify_tdengine_deployment.py`
- **What**: Diagnostic script verifying deployment
- **Who should run**: Anyone deploying or troubleshooting
- **When to run**: After bringing containers up
- **How to run**:
  ```bash
  python verify_tdengine_deployment.py
  ```
- **What it checks**:
  - Docker installation and daemon
  - Container status and health
  - TDengine connectivity
  - Database and table creation
  - Cache read/write operations

#### 6. Real-time Monitoring
**File**: `monitor_cache_stats.py`
- **What**: Continuous cache statistics monitoring
- **Who should use**: Operations, performance analysts
- **When to use**: During testing, in production, for analysis
- **How to run**:
  ```bash
  # Continuous monitoring (updates every 5 seconds)
  python monitor_cache_stats.py

  # Single snapshot
  python monitor_cache_stats.py --once

  # Custom interval (10 seconds)
  python monitor_cache_stats.py --interval 10
  ```
- **Metrics tracked**:
  - Total cached records
  - Unique symbols in cache
  - Cache hit rate (target ≥80%)
  - Hot symbols (top 10)
  - System uptime

#### 7. Quick Reference
**File**: `TDENGINE_QUICK_REFERENCE.md`
- **What**: Developer-friendly API reference
- **Who should use**: Developers integrating cache in code
- **When to reference**: While writing API endpoints
- **Key sections**:
  - Quick Start (lines 8-17)
  - API Reference (lines 19-150)
  - Complete Workflow Example (lines 152-223)
  - Error Handling (lines 265-310)
  - Best Practices (lines 318-345)

---

### 🟢 Reference Files (For Context)

#### 8. Completion Report
**File**: `TASK_2_1_COMPLETION_REPORT.md`
- **What**: Detailed analysis of what was delivered
- **Purpose**: Documentation and knowledge transfer
- **When to read**: For understanding implementation details
- **Key sections**:
  - Executive Summary (lines 8-22)
  - Verification Checklist (lines 24-42)
  - Deliverables Summary (lines 44-95)
  - Code Quality Metrics (lines 97-115)
  - Usage Examples (lines 117-185)

#### 9. Implementation Plan
**File**: `TASK_2_IMPLEMENTATION_PLAN.md`
- **What**: 4-week roadmap for Task 2
- **Purpose**: Understanding overall task structure
- **When to read**: For context on what comes next
- **Key sections**:
  - Task Breakdown (lines 21-58)
  - Data Architecture (lines 60-97)
  - Success Metrics (lines 131-137)
  - Next Steps (lines 141-143)

#### 10. Session Summary
**File**: `SESSION_COMPLETION_2025_11_06.md`
- **What**: Overall session progress and accomplishments
- **Purpose**: Context for multi-session projects
- **When to read**: At start of new session to understand previous work
- **Key sections**:
  - What Was Accomplished (lines 9-100)
  - Deliverables Summary (lines 102-125)
  - Technical Highlights (lines 127-175)
  - How to Continue (lines 180-210)

#### 11. TaskMaster Status
**File**: `.taskmaster/tasks/tasks.json`
- **What**: Task tracking and status database
- **Status**: Updated to mark 2.1 as "done"
- **How to update**:
  ```bash
  task-master set-status --id=2.1 --status=done
  ```

---

## 🗺️ Navigation by Use Case

### "I need to deploy TDengine"
1. Read: `TASK_2_1_DEPLOYMENT_GUIDE.md` (lines 10-45)
2. Run: `docker-compose -f docker-compose.tdengine.yml up -d`
3. Verify: `python verify_tdengine_deployment.py`

### "I need to use the cache in my API endpoint"
1. Read: `TDENGINE_QUICK_REFERENCE.md`
2. Reference: `web/backend/app/core/tdengine_manager.py` (lines 35-56)
3. Example: `web/backend/tests/test_tdengine_manager.py::TestCacheWriteOperations`

### "Something broke during deployment"
1. Run: `python verify_tdengine_deployment.py`
2. Read: `TASK_2_1_DEPLOYMENT_GUIDE.md` (lines 267-310)
3. Check: `docker-compose -f docker-compose.tdengine.yml logs tdengine`

### "I need to monitor cache performance"
1. Run: `python monitor_cache_stats.py`
2. Reference: `TASK_2_1_DEPLOYMENT_GUIDE.md` (lines 95-130)
3. Report: Review metrics every 5 seconds

### "I want to understand what was delivered"
1. Read: `SESSION_COMPLETION_2025_11_06.md`
2. Details: `TASK_2_1_COMPLETION_REPORT.md`
3. Code: `web/backend/app/core/tdengine_manager.py`

### "Tests are failing"
1. Run: `pytest web/backend/tests/test_tdengine_manager.py -vv`
2. Check: `docker ps | grep tdengine` (is it running?)
3. Debug: `python verify_tdengine_deployment.py`
4. Reference: Test code in `web/backend/tests/test_tdengine_manager.py`

### "I need to implement Subtask 2.2 (cache read/write logic)"
1. Start: `python verify_tdengine_deployment.py` (verify 2.1 works)
2. Reference: `TDENGINE_QUICK_REFERENCE.md`
3. Plan: `TASK_2_IMPLEMENTATION_PLAN.md` (lines 35-41)
4. Code: Build API endpoints using TDengineManager
5. Test: Add tests following pattern from `test_tdengine_manager.py`

---

## 📊 Code Organization

### Core Module Structure
```
web/backend/
├── app/
│   └── core/
│       ├── tdengine_manager.py          (474 lines)
│       ├── unified_email_service.py     (from Phase 2)
│       ├── unified_market_data_service.py (from Phase 2)
│       └── adapter_factory.py           (from Phase 2)
└── tests/
    └── test_tdengine_manager.py         (650+ lines)
```

### Entry Point
```python
# Import the manager
from web.backend.app.core.tdengine_manager import get_tdengine_manager

# Get singleton instance
manager = get_tdengine_manager()

# Use in your code
data = manager.read_cache(symbol="000001", data_type="fund_flow")
```

---

## 🔄 Dependencies Between Files

```
tdengine_manager.py (core)
    ↓
    ├── Imported by: verify_tdengine_deployment.py
    ├── Imported by: monitor_cache_stats.py
    ├── Imported by: test_tdengine_manager.py
    └── Imported by: Future API endpoints (Subtask 2.2)

docker-compose.tdengine.yml (infrastructure)
    ↓
    └── Used by: verify_tdengine_deployment.py
    └── Used by: monitor_cache_stats.py
    └── Used by: Development/testing

test_tdengine_manager.py (validation)
    ↓
    └── Tests: tdengine_manager.py
```

---

## 📝 Documentation Cross-References

### TDENGINE_QUICK_REFERENCE.md references:
- Source code: `web/backend/app/core/tdengine_manager.py`
- Tests: `web/backend/tests/test_tdengine_manager.py`
- Deployment: `TASK_2_1_DEPLOYMENT_GUIDE.md`

### TASK_2_1_DEPLOYMENT_GUIDE.md references:
- Docker config: `docker-compose.tdengine.yml`
- Verification: `verify_tdengine_deployment.py`
- Monitoring: `monitor_cache_stats.py`
- Implementation: `TASK_2_IMPLEMENTATION_PLAN.md`

### TASK_2_1_COMPLETION_REPORT.md references:
- Implementation: `web/backend/app/core/tdengine_manager.py`
- Tests: `web/backend/tests/test_tdengine_manager.py`
- Deployment: `TASK_2_1_DEPLOYMENT_GUIDE.md`
- Testing: `verify_tdengine_deployment.py`

---

## 🎯 Next Steps for Subtask 2.2

To implement the next subtask (cache read/write logic integration):

1. **Verify 2.1 is complete**:
   ```bash
   python verify_tdengine_deployment.py
   pytest web/backend/tests/test_tdengine_manager.py -v
   ```

2. **Reference files for implementation**:
   - API pattern: `TDENGINE_QUICK_REFERENCE.md`
   - Test patterns: `web/backend/tests/test_tdengine_manager.py`
   - Existing services: `web/backend/app/core/unified_market_data_service.py`

3. **Create API endpoints**:
   - Use `get_tdengine_manager()` to get manager instance
   - Implement cache-aside pattern (read, if miss, fetch and write)
   - Follow existing API patterns

4. **Add tests**:
   - Follow test patterns from `test_tdengine_manager.py`
   - Test both cache hit and miss scenarios
   - Test integration with UnifiedMarketDataService

5. **Update task status**:
   ```bash
   task-master set-status --id=2.2 --status=done
   task-master next  # Get next task
   ```

---

## 📚 Summary Table

| Category | File | Size | Status | Action |
|----------|------|------|--------|--------|
| **Implementation** | tdengine_manager.py | 474 L | ✅ Ready | Use in endpoints |
| **Testing** | test_tdengine_manager.py | 650+ L | ✅ Ready | Run tests |
| **Infrastructure** | docker-compose.tdengine.yml | 82 L | ✅ Ready | Deploy |
| **Validation** | verify_tdengine_deployment.py | 420+ L | ✅ Ready | Run verification |
| **Monitoring** | monitor_cache_stats.py | 350+ L | ✅ Ready | Monitor performance |
| **Documentation** | TASK_2_1_DEPLOYMENT_GUIDE.md | 500+ L | ✅ Ready | Read first |
| **Reference** | TDENGINE_QUICK_REFERENCE.md | 300+ L | ✅ Ready | Reference while coding |
| **Report** | TASK_2_1_COMPLETION_REPORT.md | 500+ L | ✅ Ready | Understanding |
| **Plan** | TASK_2_IMPLEMENTATION_PLAN.md | 146 L | ✅ Ready | Context |
| **Summary** | SESSION_COMPLETION_2025_11_06.md | 400+ L | ✅ Ready | Session context |

---

*Navigation Guide for Task 2.1 - 2025-11-06*
*Total files: 11 | Total lines: 5,200+ | Status: COMPLETE ✅*
