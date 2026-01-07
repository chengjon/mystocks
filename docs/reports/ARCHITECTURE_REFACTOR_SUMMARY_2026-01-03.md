# 架构重构与 Saga 分布式事务实施总结报告

**日期**: 2026-01-03
**状态**: ✅ 已实施 (Implemented)
**涉及模块**: Core, DataAccess, Infrastructure, Cron

---

## 1. 重构概览

本次架构重构旨在解决 MyStocks 系统中阻碍稳定性与可维护性的三大核心挑战。通过引入**增强型 Saga 事务模式**、**职责分离**和**依赖注入**，显著提升了系统的一致性和解耦程度。

| 挑战 | 解决方案 | 核心组件 |
| :--- | :--- | :--- |
| **跨数据库事务缺失** | **应用层 Saga 模式** (增强型)<br>采用"先写 TDengine 后写 PG"策略，利用 Tags 实现软补偿。 | `SagaCoordinator`<br>`TransactionCleaner`<br>`transaction_log` (PG Table) |
| **过度封装与混合职责** | **拆分 DataManager**<br>将路由、适配器管理职责剥离，DataManager 转变为纯粹的协调者。 | `DataRouter`<br>`AdapterRegistry`<br>`DataManager` (Refactored) |
| **模块耦合度高** | **事件驱动与依赖注入**<br>移除硬编码依赖，引入 EventBus 解耦监控逻辑。 | `EventBus`<br>`DataManager` (DI Support) |

---

## 2. 详细变更清单

### 2.1 新增基础设施组件 (`src/core/infrastructure/`)
- **`data_router.py`**: 封装数据分类到数据库目标的路由策略（原 DataManager._ROUTING_MAP）。
- **`adapter_registry.py`**: 统一管理数据源适配器的注册与生命周期。
- **`event_bus.py`**: 简单的同步事件总线，用于解耦业务逻辑与监控/日志系统。

### 2.2 新增事务组件 (`src/core/transaction/`)
- **`saga_coordinator.py`**: Saga 事务的核心协调器。负责执行 "TDengine Write -> PG Update" 的原子化流程，并处理瞬时失败的补偿逻辑。

### 2.3 核心类重构 (`src/core/data_manager.py`)
- **`DataManager`**:
    - **移除**: 内部硬编码的路由表、适配器字典、直接的监控调用。
    - **新增**: 支持构造函数依赖注入（Router, Registry, EventBus, DataAccess）。
    - **新增**: 集成 `SagaCoordinator`，支持通过 `use_saga=True` 参数开启分布式事务模式。
    - **兼容**: 保持 `save_data` / `load_data` API 签名不变，确保向后兼容。

### 2.4 数据访问层增强 (`src/data_access/`)
- **`tdengine_access.py`**:
    - 新增 `save_data(..., extra_tags=...)`: 支持写入时携带事务 ID (`txn_id`) 和有效性标记 (`is_valid`)。
    - 新增 `invalidate_data_by_txn_id(...)`: 实现基于 Tag 修改的软删除补偿逻辑。
- **`postgresql_access.py`**:
    - 新增 `transaction_scope()`: 上下文管理器，支持事务的自动提交与回滚。

### 2.5 运维与清理 (`src/cron/` & `scripts/`)
- **`src/cron/transaction_cleaner.py`**: 定时任务，扫描 PG 状态表，清理僵尸事务并执行最终一致性补偿。
- **`scripts/migrations/migrate_tdengine_tags.py`**: 自动生成 SQL，为所有 TDengine 超级表添加 `txn_id` 和 `is_valid` 标签。
- **`scripts/migrations/create_pg_transaction_log.sql`**: 创建 PostgreSQL 事务状态表。

---

## 3. 增强型 Saga 事务机制

鉴于 TDengine 不支持传统事务回滚，我们采用了**向前恢复 + 软补偿**策略。

### 3.1 核心流程
1.  **初始化**: 生成 `txn_id`，在 PG `transaction_log` 记录状态 `PENDING`。
2.  **Step 1 (TDengine)**: 写入时序数据，附带 Tag `is_valid=true`。
    *   *成功*: 更新日志 `td_status='SUCCESS'`。
    *   *失败*: 事务终止，PG 无变更，数据一致。
3.  **Step 2 (PostgreSQL)**: 更新业务元数据。
    *   *成功*: 提交 PG 事务，更新日志 `final_status='COMMITTED'`。
    *   *失败*: PG 事务回滚。此时 TDengine 有脏数据，触发**补偿**。
4.  **补偿 (Compensation)**: 调用 TDengine `ALTER TABLE ... SET TAG is_valid=false`，逻辑删除脏数据。

### 3.2 兜底机制 (The Cleaner)
定时任务每 5-10 分钟运行一次：
- 扫描 `PENDING` 超过 10 分钟的事务。
- 如果 TDengine 写入成功但 PG 未提交 -> 执行补偿 (标记无效) 并关闭事务。
- 如果处于其他中间状态 -> 标记回滚。

---

## 4. 建议后续操作 (Action Items)

为了使新架构完全生效，请执行以下操作：

### 4.1 数据库迁移 (必做)
1.  **PostgreSQL**: 执行 SQL 脚本创建状态表。
    ```bash
    psql -h $PG_HOST -U $PG_USER -d quant_research -f scripts/migrations/create_pg_transaction_log.sql
    ```
2.  **TDengine**: 生成并执行 Tag 迁移脚本。
    ```bash
    python3 scripts/migrations/migrate_tdengine_tags.py > migrate.sql
    # 检查 migrate.sql 内容无误后，在 taos 客户端执行
    taos -f migrate.sql
    ```

### 4.2 部署定时任务
配置 Crontab 以运行清理任务（建议每 5 分钟）：
```cron
*/5 * * * * /usr/bin/python3 /opt/claude/mystocks_spec/src/cron/transaction_cleaner.py >> /var/log/mystocks_cleaner.log 2>&1
```

### 4.3 代码质量治理 (P0)
- **静态检查**: 运行 `pylint src/core/` 检查新代码是否引入了新的 Lint 错误。
- **单元测试**: 为 `DataRouter`, `AdapterRegistry`, `SagaCoordinator` 编写单元测试，目标覆盖率 > 80%。

### 4.4 业务迁移
- 逐步将现有的双写业务逻辑（如 K 线同步任务）迁移到使用 `DataManager.save_data(..., use_saga=True)`。

---

**文档生成**: Claude (Architecture Specialist)
**生成时间**: 2026-01-03
