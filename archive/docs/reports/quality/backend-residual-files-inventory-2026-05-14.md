# MyStocks 后端备份/残留文件清册

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §二.4 + §四.2 深化
> **审计日期**: 2026-05-14
> **重扫校准**: 2026-05-15（代码事实已验证）
> **审计范围**: `web/backend/` 全量扫描
> **判定标准**: `architecture/STANDARDS.md` §三.3「兼容层、临时层与机械拆分约束」

---

## 〇、2026-05-15 重扫执行记录

已删除 9 个文件（代码路径判定通过，无 import 引用）：

| # | 已删除文件 | 原类别 | 判定依据 |
|---|-----------|--------|----------|
| 1 | `api/mystocks_complete.py.bak` | .bak | 无 import，canonical `mystocks_complete.py` 不存在（整文件是历史备份） |
| 2 | `api/risk_management.py.bak` | .bak | 无 import，canonical `risk_management.py` 存在 |
| 3 | `api/strategy_management.py.backup` | .backup | 无 import，canonical `strategy_management/` package 存在 |
| 4 | `api/data_source_config.py.backup` | .backup | 无 import，canonical `data_source_config.py` 存在 |
| 5 | `api/data_source_config.old.py` | .old | 无 import，canonical 存在 |
| 6 | `services/data_adapter.py.backup.20260130` | .backup+date | 无 import，canonical 存在 |
| 7 | `services/watchlist_service.py.bak2` | .bak2 | 无 import，canonical 存在，git 历史可追溯 |
| 8 | `services/watchlist_service.py.bak3` | .bak3 | 无 import，canonical 存在，git 历史可追溯 |
| 9 | `services/watchlist_service.py.before_schema_update` | .before_* | 无 import，canonical 存在 |

保留 1 个文件（有 import 引用）：

| 文件 | 原因 |
|------|------|
| `api/auth_compat.py` | 被 `tests/test_auth_login_contract.py` 引用，需先更新测试 |

---

## 一、发现汇总（重扫后更新）

| 类别 | 原数量 | 已处理 | 剩余 |
|------|--------|--------|------|
| 备份文件 (`.bak`/`.backup`/`.before_*`) | 4 | 4 ✅ 已删除 | 0 |
| 旧版本 (`.old.py`) | 1 | 1 ✅ 已删除 | 0 |
| 兼容 shim (`_compat.py`) | 1 | 0 | 1（`auth_compat.py`，需更新测试） |
| 新版本过渡 (`_new.py`) | 4 | 0 | 4（需迁移计划） |
| Core 重复文件 | 5 组 | 0 | 5（需 OpenSpec） |

---

## 二、逐文件清册

### 2.1 备份文件 — 删除候选（4 个）

这些文件是曾用版本的备份，当前 canonical 文件均存在且活跃。它们仍需按 `architecture/STANDARDS.md` 完成代码路径判定和功能树判定后才能删除。

| # | 文件路径 | 大小 | 备份原因 | 当前 canonical | 判定 |
|---|----------|------|----------|----------------|------|
| 1 | `app/services/watchlist_service.py.bak2` | ~30KB | 第二次重构前备份 | `app/services/watchlist_service.py` ✅ 存在 | **待双判定** |
| 2 | `app/services/watchlist_service.py.bak3` | ~30KB | 第三次重构前备份 | 同上 | **待双判定** |
| 3 | `app/services/watchlist_service.py.before_schema_update` | ~30KB | Schema 更新前快照 | 同上 | **待双判定** |
| 4 | `app/services/data_adapter.py.backup.20260130` | ~15KB | 2026-01-30 重构前备份 | `app/services/data_adapter.py` ✅ 存在 | **待双判定** |

> ⚠️ `watchlist_service.py` 有三个不同时期的备份，说明经历了多次重构。删除前确认 git 历史已保留变更记录。

### 2.2 旧版本文件（3 个）

| # | 文件路径 | 描述 | canonical | 判定 |
|---|----------|------|-----------|------|
| 5 | `app/api/data_source_config.old.py` | 数据源配置 API 旧版 | `app/api/data_source_config.py` ✅ 存在 | **可删除** |
| 6 | `app/api/data_source_config.py.backup` | 数据源配置 API 备份 | `app/api/data_source_config.py` ✅ 存在 | **可删除** |
| 7 | `app/api/monitoring_old/` *(目录，2 文件)* | 旧版监控路由 (`routes.py` + `__init__.py`) | `app/api/monitoring.py` ✅ 存在，但需确认 `monitoring_old/` 是否仍被路由注册引用 | **需确认后删除** |

> ⚠️ `monitoring_old/` 的 `router` 若仍在 `router_registry.py` 或别处被 `include_router` 注册，则不能直接删除目录。需先移除注册引用。

### 2.3 `_new.py` 过渡文件（4 个）

这些是重构过程中创建的"新版"文件，与对应的旧文件并存，违反了 STANDARDS.md §三.1「同一职责只允许一个主实现」。

| # | 新版文件 | 旧版文件 | 状态 | 判定 |
|---|----------|----------|------|------|
| 8 | `app/services/data_adapter_new.py` | `app/services/data_adapter.py` | 新版作为兼容层，导入自 `adapters_split/` | **需合并**：若新版已稳定，用新版替换旧版后删除 |
| 9 | `app/services/data_api_new.py` | `app/api/data/data_api_new.py` *(也存在同文件)* | ⚠️ 两个位置各有一份 `data_api_new.py` | **需决策**：确定哪个是 canonical，删除另一个 |
| 10 | `app/api/data/data_api_new.py` | 同上 `app/services/data_api_new.py` | 与 services 下的同名文件重复 | **需决策**：二选一 |
| 11 | `app/services/risk_management_new.py` | `app/services/risk_management.py` *(不存在于 services，但 api/ 下有 `risk_management.py`)* | 新版风控服务 | **需合并**：确认 canonical 位置后替换 |

> ⚠️ `data_api_new.py` 在 `app/api/data/` 和 `app/services/` 各有一份，需确认是否相同文件、哪个是正本。

### 2.4 版本迭代文件（3 个）

| # | 文件 | 描述 | 判定 |
|---|------|------|------|
| 12 | `app/services/risk_management_2.py` | 风控服务第 2 版，与 `risk_management_new.py` 关系不明 | **需合并**：三选一 canonical |
| 13 | `app/services/data_service_enhanced.py` | 增强版数据服务，与 `data_service.py` 共存 | **需合并**：若 `_enhanced` 覆盖了旧版功能，替换旧版 |
| 14 | `app/adapters/eastmoney_enhanced.py` | 增强版东方财富适配器 | **保留**：作为独立 adapter，不是旧版替代 |

### 2.5 机械拆分文件 — 违反 STANDARDS.md §三.3（5 个）

STANDARDS.md 明确规定：「禁止机械拆分，`part1.py`、`part2.py`、`part3.py` 不得作为长期结构」。

| # | 文件 | 所属模块 | 判定 |
|---|------|----------|------|
| 15 | `app/repositories/algorithm_model_repository/algorithm_model_repository_methods/part1.py` | 算法模型仓库 | **需按职责重拆分** |
| 16 | `app/repositories/algorithm_model_repository/algorithm_model_repository_methods/part2.py` | 同上 | **需按职责重拆分** |
| 17 | `app/repositories/algorithm_model_repository/algorithm_model_repository_methods/part3.py` | 同上 | **需按职责重拆分** |
| 18 | `app/services/market_data_service/market_data_service_methods/part1.py` | 市场数据服务 | **需按职责重拆分** |
| 19 | `app/services/market_data_service/market_data_service_methods/part2.py` | 同上 | **需按职责重拆分** |

### 2.6 Core 层重复文件（5 组 — 详见 F 方案）

已在 `docs/reports/quality/backend-core-split-plan-2026-05-14.md` §四详述：

| 组 | 文件 | 判定 |
|----|------|------|
| 20 | `exception_handler.py` / `exception_handlers.py` / `global_exception_handlers.py` | 归并为 1 canonical + 1 decorator |
| 21 | `validation.py` / `validators.py` | 合并为 `validation/core.py` |
| 22 | `cache_manager.py` / `cache_utils.py` | 同名 `CacheManager` 类冲突，需区分或合并 |
| 23 | `database_performance.py` / `database_performance_monitor.py` | 合并 |
| 24 | `tdengine_manager.py` / `tdengine_pool.py` | 合并 |

---

## 三、执行建议

### 🔴 立即执行前置项（禁止直接删除）

```bash
# 1. 重新扫描当前工作树
find web/backend/app -type f \( -name "*.bak*" -o -name "*.backup*" -o -name "*.old.py" \)

# 2. 对每个候选对象补双判定表
# - 代码路径判定
# - 功能树判定
# - 兼容职责
# - 删除或保留依据
```

只有双判定表确认“代码路径可安全移除”且“功能树状态为重复冗余或正式下线”后，才能在单独提交中删除候选文件。

### 🟡 需 1 次确认后执行

```bash
# 3. 确认 monitoring_old 无活跃引用后删除
grep -r "monitoring_old" web/backend/app/ --include="*.py"
# 若无输出，则可删除：
rm -rf app/api/monitoring_old/
```

### 🟢 需方案评审后执行

| 项 | 行动 | 负责人 |
|----|------|--------|
| `_new.py` 文件 4 个 | 逐一确认新旧版差异，选择 canonical，删除冗余 | 后端 owner |
| `_2.py` / `_enhanced.py` 3 个 | 确认功能覆盖，合并或保留 | 后端 owner |
| `part1/part2/part3` 机械拆分 5 个 | 按语义职责重新拆分，重构后移除 partN 文件 | 相关模块 owner |
| Core 重复 5 组 | 按 Core 拆分方案执行 | 架构 owner |

---

## 四、本次审计与原始审计的差异说明

原始审计报告（`backend-audit-2026-05-14.md`）中列出的部分文件在 2026-05-15 复核时与本文结论不一致，因此本节标记为待重扫：

| 原始声称 | 实际状态 |
|----------|----------|
| `api/strategy_management.py.backup` | 2026-05-15 复核显示当前工作树存在，需重新纳入清册 |
| `api/risk_management.py.bak` | 2026-05-15 复核显示当前工作树存在，需重新纳入清册 |
| `api/mystocks_complete.py.bak` | 2026-05-15 复核显示当前工作树存在，需重新纳入清册 |
| `api/auth_compat.py` | ⚠️ 存在但属于功能性兼容 shim，非备份/残留，不移除 |

本清册必须重新扫描后再作为执行依据。当前版本只能作为历史审计快照。

---

## 五、统计

| 统计项 | 数量 |
|--------|------|
| 可立即删除 | **6 个文件** |
| 确认后删除 | **1 目录（2 文件）** |
| 需合并/迁移 | **17 项**（5 `_new` + 3 `_enhanced` + 5 partN + 5 Core 组，部分跨文档覆盖） |
| 扫描范围 | `web/backend/` 全目录 |
| 判定依据 | `architecture/STANDARDS.md` §三 |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §二.4 + §四.2*
