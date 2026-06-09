# PHASE 2: Saga 分布式事务落地与生产化任务清单

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


## 🎯 目标
将跨库一致性方案从 Demo 提升至生产级，完成核心业务迁移并建立全方位监控。

**当前状态**: 🟡 部分完成（已存在测试与仪表盘，但缺少 transaction_log 实写、duration_ms 字段、告警规则与业务接入路径更新）

---

## 🛠️ 第一阶段：验证与观测 (本周重点)
- [x] **扩展测试覆盖**
    - [x] `tests/core/transaction/test_saga_tick_data.py` (Tick 写入与补偿)
    - [x] `tests/core/transaction/test_saga_concurrency.py` (并发压力测试)
- [ ] **监控集成 (Grafana + PG) - 部分完成**
    - [x] `transaction_log` 建表脚本已存在: `scripts/migrations/create_pg_transaction_log.sql`
    - [x] `error_msg` / `retry_count` 字段已存在
    - [ ] **补充 `duration_ms` 字段** (脚本当前缺失)
    - [ ] **Saga 事务实写 `transaction_log`** (当前仅注释/日志，需在 `src/core/transaction/saga_coordinator.py` 接入)
    - [x] Grafana Dashboard JSON 已存在: `config/grafana/dashboards/saga_transactions.json`
    - [ ] Prometheus/Alertmanager 告警规则 (未发现 Saga 相关规则，需新增)

## 🔄 第二阶段：核心业务迁移
- [ ] **K线同步迁移（路径需更新）**
    - [ ] 原路径 `src/data_sources/real/kline_syncer.py` 不存在，需先定位真实落库入口
    - [ ] 建议从 `save_data_by_classification` / `save_data` 的调用处下手，明确 K 线写入链路
    - [ ] 在入口处启用 `use_saga=True` 并提供 `metadata_callback` 完成 PG 元数据写入
    - [ ] 验证全量同步场景下的事务稳定性
- [ ] **实时行情迁移（需重新评估 Saga 适用性）**
    - [ ] 当前实时行情写入入口示例: `src/storage/database/save_realtime_market_data.py` (统一管理器 → PG/Redis)
    - [ ] 若不涉及 TDengine+PG 双写，则无需 Saga；如需跨库一致性，再接入 `use_saga`
    - [ ] 评估高频写入下的延迟开销 (Latency Overhead)

## 🧹 第三阶段：治理与优化
- [ ] **架构清理**
    - [ ] 移除冗余的 `src/storage/access/` 目录（当前仅在 `src/README.md` 中被提及，删除前确认无引用）
    - [ ] 统一所有 DataAccess 的日志标准 (EventBus)（DataManager 已有事件机制，DataAccess 尚未统一）
- [ ] **自动化清理任务**
    - [ ] 激活 `src/cron/transaction_cleaner.py`（代码已存在，需部署级启用）
    - [ ] 补全 transaction_cleaner 的 **真实查询/删除逻辑**（当前为示例/占位）
    - [ ] 定期物理删除 TDengine 中 `is_valid=false` 的历史碎片数据（可通过 `--purge`）

---
**当前进度**: 🟢 启动中
**负责人**: Gemini CLI Agent
