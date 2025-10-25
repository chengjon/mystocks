# 代码重复分析摘要

**总重复案例**: 20

## 严重性分布

- CRITICAL: 1 案例
- HIGH: 12 案例
- MEDIUM: 7 案例
- LOW: 0 案例

## 🔴 需要立即处理的重复

### 1. DUP-63cd6c5e
- **严重性**: CRITICAL
- **相似度**: Token 97%, AST 100%
- **位置**: 2 处
  - `web/backend/app/api/auth.py:191`
  - `web/backend/app/core/security.py:136`

### 2. DUP-40cc37bc
- **严重性**: HIGH
- **相似度**: Token 84%, AST 91%
- **位置**: 2 处
  - `run_realtime_market_saver.py:29`
  - `db_manager/validate_mystocks_architecture.py:31`

### 3. DUP-047d1d49
- **严重性**: HIGH
- **相似度**: Token 81%, AST 92%
- **位置**: 2 处
  - `web/backend/app/main.py:86`
  - `web/backend/app/api/market.py:346`

### 4. DUP-bc8ece80
- **严重性**: HIGH
- **相似度**: Token 92%, AST 98%
- **位置**: 2 处
  - `tests/acceptance/test_us2_config_driven.py:538`
  - `tests/unit/test_postgresql_table_creation.py:223`

### 5. DUP-bc8ece80
- **严重性**: HIGH
- **相似度**: Token 92%, AST 98%
- **位置**: 2 处
  - `tests/acceptance/test_us2_config_driven.py:538`
  - `tests/unit/test_mysql_table_creation.py:245`
