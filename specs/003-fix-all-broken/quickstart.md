# Quick Start Guide

**Feature**: Fix All Broken Web Features
**Branch**: `003-fix-all-broken`
**Date**: 2025-10-25

## Overview

This guide helps developers quickly set up their environment and start fixing broken features in the MyStocks web application.

---

## Prerequisites

### Required Software

- **Python**: 3.8+ (recommended: 3.10)
- **Node.js**: 18+ with npm
- **PostgreSQL**: 14+
- **TDengine**: 3.0+
- **Git**: Latest version

### Optional Tools

- **Docker**: For isolated database setup
- **VS Code**: Recommended IDE with Python and Vue extensions

---

## Initial Setup

### 1. Clone and Checkout Branch

```bash
cd /opt/claude/mystocks_spec
git checkout 003-fix-all-broken
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r web/backend/requirements.txt

# Set up environment variables
cp deployment/production.env.template .env
nano .env  # Edit database credentials

# Verify database connections
python -c "from app.core.database import get_postgresql_engine; print('PostgreSQL OK')"
python -c "import taos; taos.connect(host='localhost'); print('TDengine OK')"
```

### 3. Frontend Setup

```bash
cd web/frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Backend Server

```bash
cd web/backend

# Run with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Verification Steps

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api/docs
```

### 2. Test Frontend

```bash
# Open browser
open http://localhost:5173

# Login with test credentials
# Username: test@mystocks.com
# Password: test123
```

### 3. Test Database Connectivity

```bash
# PostgreSQL
PGPASSWORD=your_password psql -h localhost -U postgres -d mystocks -c "SELECT COUNT(*) FROM stocks_basic;"

# TDengine
taos -h localhost -s "USE market_data; SELECT COUNT(*) FROM tick_data;"
```

---

## Development Workflow

### Fixing a Broken Feature

1. **Identify the Issue**
   ```bash
   # Read the code review report
   cat COMPREHENSIVE_CODE_REVIEW_REPORT.md | grep "BROKEN"
   ```

2. **Locate Affected Files**
   ```bash
   # Backend
   ls web/backend/app/api/data.py  # db_service undefined issue
   ls web/backend/app/core/database.py  # Missing db_service

   # Frontend
   ls web/frontend/src/views/Dashboard.vue  # Mock data issue
   ls web/frontend/src/components/market/FundFlowPanel.vue  # MySQL dependency
   ```

3. **Make Changes Following Code Modification Rules**
   ```bash
   # Read modification rules
   cat 代码修改规则-new.md

   # Key principles:
   # - Minimal changes only
   # - No protected modules
   # - Architecture compliance
   # - Add tests for fixes
   ```

4. **Test Changes**
   ```bash
   # Backend unit tests
   cd web/backend
   pytest tests/ -v

   # Frontend component tests
   cd web/frontend
   npm run test

   # E2E tests (after implementation)
   npm run test:e2e
   ```

5. **Commit with Standard Format**
   ```bash
   git add web/backend/app/core/database.py
   git commit -m "[BUGFIX] Add db_service to database.py (fix-web-features#001)

   - Implement get_unified_manager() singleton
   - Create db_service alias for backwards compatibility
   - Resolves NameError in app/api/data.py

   Related: Issue #35 in code review report"
   ```

---

## Common Tasks

### Task 1: Fix db_service Undefined Error

**File**: `web/backend/app/core/database.py`

```python
# Add to database.py
from core.unified_manager import MyStocksUnifiedManager

_unified_manager = None

def get_unified_manager() -> MyStocksUnifiedManager:
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = MyStocksUnifiedManager(enable_cache=True)
    return _unified_manager

# Backwards compatibility alias
db_service = get_unified_manager()
```

**Test**:
```bash
curl http://localhost:8000/api/data/stocks/basic | jq '.code'
# Should return 200
```

### Task 2: Migrate MySQL Table to PostgreSQL

**Step 1**: Export data
```bash
mysql -h localhost -u root -p mystocks -e "SELECT * FROM fund_flow INTO OUTFILE '/tmp/fund_flow.csv'  FIELDS TERMINATED BY ',' ENCLOSED BY '\"';"
```

**Step 2**: Update table_config.yaml
```yaml
- table_name: fund_flow
  database_target: postgresql
  classification: market_metadata
  # ... (see data-model.md for full schema)
```

**Step 3**: Create table
```bash
python -c "from db_manager.database_manager import DatabaseTableManager;
mgr = DatabaseTableManager();
mgr.batch_create_tables('table_config.yaml')"
```

**Step 4**: Import data
```bash
psql -h localhost -U postgres -d mystocks -c "\\COPY fund_flow FROM '/tmp/fund_flow.csv' WITH CSV HEADER"
```

**Step 5**: Verify
```bash
psql -h localhost -U postgres -d mystocks -c "SELECT COUNT(*) FROM fund_flow;"
```

### Task 3: Connect Dashboard to Real Data

**File**: `web/frontend/src/views/Dashboard.vue`

```javascript
// Replace mock data
const favoriteStocks = ref([])

// Add API call
const loadFavoriteStocks = async () => {
  try {
    const response = await dataApi.getDashboardSummary({ include: ['favorites'] })
    favoriteStocks.value = response.data.favorites
  } catch (error) {
    ElMessage.error('Failed to load favorite stocks')
  }
}

onMounted(() => {
  loadFavoriteStocks()
})
```

**Test**:
- Open http://localhost:5173/dashboard
- Verify real stock data appears (not "600519 贵州茅台")
- Check network tab shows API call to `/api/data/dashboard/summary`

---

## Running Tests

### Backend Tests

```bash
cd web/backend

# All tests
pytest tests/ -v

# Specific module
pytest tests/test_api_endpoints.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend Tests

```bash
cd web/frontend

# Unit tests
npm run test

# E2E tests (chrome-devtools-mcp)
npm run test:e2e

# Watch mode
npm run test:watch
```

### E2E Tests (Manual)

```bash
# 1. Start both servers
# Terminal 1:
cd web/backend && uvicorn app.main:app --reload

# Terminal 2:
cd web/frontend && npm run dev

# 2. Test critical flows
# - Login → Dashboard → Verify real data
# - Navigate to Fund Flow → Verify data loads
# - Create indicator config → Save → Reload page → Verify persisted
```

---

## Debugging Tips

### Backend Issues

```bash
# Check logs
tail -f web/backend/logs/error.log

# Interactive debugging with ipdb
pip install ipdb
# Add: import ipdb; ipdb.set_trace()

# Test specific endpoint
curl -X GET "http://localhost:8000/api/data/stocks/basic?limit=10" -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Issues

```bash
# Check browser console (F12)
# Look for errors in Network tab

# Vue DevTools
# Install browser extension: Vue.js devtools

# Check API responses
# Network tab → Filter: XHR → Click request → Preview tab
```

### Database Issues

```bash
# PostgreSQL
psql -h localhost -U postgres -d mystocks

# List tables
\dt

# Check table structure
\d fund_flow

# Query data
SELECT * FROM fund_flow LIMIT 10;

# TDengine
taos -h localhost
USE market_data;
SHOW TABLES;
SELECT COUNT(*) FROM tick_data WHERE ts > NOW() - 1d;
```

---

## Troubleshooting

### Error: "db_service is not defined"

**Solution**: Implement get_unified_manager() in `web/backend/app/core/database.py`

### Error: "MySQL connection failed"

**Solution**: Complete MySQL → PostgreSQL migration for affected tables

### Error: "Dashboard shows mock data"

**Solution**: Connect Dashboard.vue to `/api/data/dashboard/summary` endpoint

### Error: "Token expired"

**Solution**: Implement token refresh in `web/frontend/src/stores/auth.js`

---

## Next Steps

1. **Read Code Review Report**: `COMPREHENSIVE_CODE_REVIEW_REPORT.md`
2. **Follow Code Modification Rules**: `代码修改规则-new.md`
3. **Review Technical Decisions**: `research.md`
4. **Check Data Model**: `data-model.md`
5. **Study API Contracts**: `contracts/api-endpoints.md`
6. **Start Implementation**: Use `/speckit.tasks` to generate task breakdown

---

## Support Resources

- **Documentation**: `/docs/`
- **API Docs**: http://localhost:8000/api/docs
- **Code Review**: `COMPREHENSIVE_CODE_REVIEW_REPORT.md`
- **Spec**: `spec.md`
- **Plan**: `plan.md`
