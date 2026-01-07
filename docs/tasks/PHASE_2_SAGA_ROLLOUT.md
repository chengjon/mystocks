# PHASE 2: Saga 分布式事务落地与生产化任务清单

## 🎯 目标
将跨库一致性方案从 Demo 提升至生产级，完成核心业务迁移并建立全方位监控。

---

## 🛠️ 第一阶段：验证与观测 (本周重点)
- [ ] **扩展测试覆盖**
    - [ ] 创建 `tests/core/transaction/test_saga_tick_data.py` (验证高频 Tick 数据写入与补偿)
    - [ ] 创建 `tests/core/transaction/test_saga_concurrency.py` (50+ 并发事务压力测试)
- [ ] **监控集成 (Grafana + PG)**
    - [ ] 确保 `transaction_log` 表结构包含：`duration_ms`, `error_msg`, `retry_count`
    - [ ] 编写 Grafana Dashboard JSON 模板
    - [ ] 配置 Prometheus/Alertmanager 告警规则 (针对 ROLLED_BACK 异常激增)

## 🔄 第二阶段：核心业务迁移
- [ ] **K线同步迁移**
    - [ ] 修改 `src/data_sources/real/kline_syncer.py` 接入 Saga
    - [ ] 验证全量同步场景下的事务稳定性
- [ ] **实时行情迁移**
    - [ ] 修改 `src/data_sources/real/realtime_quotes.py` 接入 Saga
    - [ ] 评估高频写入下的延迟开销 (Latency Overhead)

## 🧹 第三阶段：治理与优化
- [ ] **架构清理**
    - [ ] 移除冗余的 `src/storage/access/` 目录
    - [ ] 统一所有 DataAccess 的日志标准 (EventBus)
- [ ] **自动化清理任务**
    - [ ] 激活 `src/cron/transaction_cleaner.py`
    - [ ] 定期物理删除 TDengine 中 `is_valid=false` 的历史碎片数据

---
**当前进度**: 🟢 启动中
**负责人**: Gemini CLI Agent
