# T037 Critical Finding: TDengine Not Running

**Date**: 2025-10-25
**Status**: 🚨 Critical Architecture Mismatch Detected
**Impact**: Blocks T037 (System Initialization Test)

---

## Discovery

While executing T037 (system initialization test), discovered that:

1. **TDengine is NOT running** on production server (192.168.123.104:6030)
   - Connection test failed: `WebSocket protocol error: Handshake not finished`
   - Service appears to be stopped or unconfigured

2. **.env file has TDengine commented out**:
   ```
   # TDengine - 未实际使用 (仅5行测试数据)
   # TDENGINE_HOST=192.168.123.104
   # TDENGINE_USER=root
   # TDENGINE_PASSWORD=taosdata
   # TDENGINE_PORT=6030
   # TDENGINE_DATABASE=market_data
   ```

3. **Code still expects TDengine**:
   - `db_manager/connection_manager.py`: Validates TDengine env vars
   - `unified_manager.py`: Instantiates `TDengineDataAccess()`
   - `data_access.py`: Contains 567-line `TDengineDataAccess` class
   - `monitoring_database.py`: References TDengine in docstrings

---

## Conflict Analysis

### Original US2 Specification
```
User Story 2: Maintain only 2 databases (TDengine + PostgreSQL) instead of 4
```

### Current Production Reality
```
Actual Architecture: 1 database (PostgreSQL only)
- MySQL: Removed (migrated 299 rows to PostgreSQL)
- Redis: Removed (was empty)
- TDengine: Removed/stopped (only 5 test rows, not in production use)
- PostgreSQL: Active and serving all data types
```

### CLAUDE.md Declaration
```
## ⚡ Week 3 Update (2025-10-19): Database Simplification

**Major Change**: System simplified from 4 databases to 1 (PostgreSQL only)

**Migration Completed**:
- ✅ TDengine removed (only 5 test rows, not in production use)
```

---

## Impact Assessment

### Immediate Impact
- **T037 cannot complete**: System initialization fails due to missing TDengine env vars
- **Code mismatch**: Application code expects 2 databases but only 1 is running
- **Documentation inconsistency**: Spec says 2 databases, reality is 1

### Technical Debt
- **Dead code**: 567 lines of `TDengineDataAccess` that cannot execute
- **Misleading logs**: System prints "2种数据库连接就绪" when only 1 is ready
- **Configuration confusion**: Developers must maintain unused TDengine code

---

## Recommended Solution

**Complete the simplification** by removing TDengine from code to match production reality.

### Rationale
1. **Production reality**: TDengine is not running and was intentionally removed
2. **CLAUDE.md guidance**: Explicitly states "PostgreSQL only"
3. **Technical debt**: Keeping unused code increases maintenance burden
4. **Consistency**: Align code with deployed architecture

### Proposed Changes (Expanded T037 Scope)

#### Phase 1: Remove TDengine from Core Files
- [ ] `connection_manager.py`: Remove TDengine from `required_vars`
- [ ] `unified_manager.py`: Remove `self.tdengine = TDengineDataAccess()`
- [ ] `data_access.py`: Delete `TDengineDataAccess` class (567 lines)
- [ ] `monitoring_database.py`: Update docstrings to remove TDengine references
- [ ] `core.py`: Remove TDengine from `DatabaseTarget` enum

#### Phase 2: Update Documentation
- [ ] Update CLAUDE.md to consistently reflect PostgreSQL-only
- [ ] Update US2_PROGRESS_REPORT to note expanded scope
- [ ] Update requirements.txt to remove `taospy>=2.7.0`

#### Phase 3: Verify System Initialization
- [ ] Run T037 test with PostgreSQL-only configuration
- [ ] Confirm all data classifications route to PostgreSQL
- [ ] Verify monitoring system works with single database

---

## Alternative Option (NOT Recommended)

**Restore TDengine** to match original US2 spec:

### Steps
1. Start TDengine service on 192.168.123.104:6030
2. Uncomment TDengine config in .env
3. Run T037 test

### Why NOT Recommended
- Goes against Week 3 simplification decision
- Adds operational complexity (backup, monitoring, maintenance)
- TDengine was removed because it had no production data (only 5 test rows)
- Team already committed to PostgreSQL-only in CLAUDE.md

---

## Decision Required

This finding requires architectural alignment:

**Option A (Recommended)**: Complete PostgreSQL-only migration
- Remove TDengine from code
- Update documentation to reflect reality
- Estimated time: 1-2 hours

**Option B (NOT Recommended)**: Restore dual-database architecture
- Start TDengine service
- Update .env to enable TDengine
- Maintain 2-database complexity
- Estimated time: 2-3 hours

---

## Conclusion

**Recommended**: Proceed with **Option A** to complete the architecture simplification initiated in Week 3. This aligns code with production reality and eliminates technical debt.

**Risk**: Low - TDengine had no production data and was already removed from deployment.

**Benefit**: Reduced complexity, better code-reality alignment, eliminates dead code.

---

**Next Action**: Await decision or proceed with Option A based on "继续" (continue) instruction.
