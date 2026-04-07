# 代码重复分析摘要

> **历史分析说明**:
> 本文件是阶段性分析、审计或评估材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


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
