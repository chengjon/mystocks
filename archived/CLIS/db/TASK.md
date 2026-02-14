# DB CLI 任务清单

**角色**: 数据库管理工程师
**职责**: 数据库优化、迁移、监控

## 当前进行中

### ✅ task-2.1: 优化数据库查询性能
- **进度**: 50%
- **下一步**: 完成索引优化，测试查询性能

## 🔴 高优先级任务

### 1. 优化时序数据查询性能
- **任务ID**: task-4.2
- **预计工时**: 16小时
- **技术栈**: TDengine, PostgreSQL, TimescaleDB, optimization
- **描述**:
  - 为TDengine高频数据表创建超级表
  - 优化时间分区策略（按天/周/月）
  - 为PostgreSQL TimescaleDB配置压缩
  - 设置数据保留策略（retention policy）
  - 创建优化索引（时间戳、股票代码）
  - 查询响应时间目标: < 100ms
  - 性能测试和基准对比

### 2. 设计并实现数据库迁移脚本
- **任务ID**: task-4.1
- **预计工时**: 14小时
- **技术栈**: PostgreSQL, TDengine, migration, versioning
- **描述**:
  - 创建数据库版本控制系统
  - 实现up/down迁移脚本
  - 支持PostgreSQL和TDengine的schema变更
  - 迁移历史记录和回滚机制
  - 数据一致性验证
  - 自动化迁移工具

## 🟡 中优先级任务

### 3. 实现数据库监控和告警
- **任务ID**: task-4.3
- **预计工时**: 10小时
- **技术栈**: Prometheus, monitoring, alerting
- **描述**:
  - 配置数据库性能监控
  - 追踪慢查询（> 1秒）
  - 监控连接池使用情况
  - 监控磁盘IO和存储空间
  - 设置告警阈值
  - 集成Prometheus exporter
  - 自动发送告警通知到main CLI

## 📋 任务依赖关系

```
task-2.1 (查询优化) ← 当前进行中
    ↓
task-4.2 (时序优化) ← 深度优化
    ↓
task-4.1 (数据库迁移) ← 基础设施
    ↓
task-4.3 (监控告警) ← 运维支持
```

## 📝 工作流程

1. ✅ **Phase 1**: 完成查询优化 (task-2.1)
   - 添加必要索引
   - 测试查询性能
   - 生成优化报告

2. ✅ **Phase 2**: 优化时序数据 (task-4.2)
   - 创建TDengine超级表
   - 配置分区策略
   - 性能测试和调优

3. ✅ **Phase 3**: 实现迁移系统 (task-4.1)
   - 设计迁移框架
   - 编写迁移脚本
   - 测试回滚机制

4. ✅ **Phase 4**: 配置监控 (task-4.3)
   - 集成Prometheus
   - 配置告警规则
   - 测试通知机制

## 🔗 相关文档

- TDengine指南: `docs/database/TDENGINE_GUIDE.md`
- PostgreSQL优化: `docs/database/POSTGRESQL_OPTIMIZATION.md`
- 迁移系统设计: `docs/database/MIGRATION_DESIGN.md`

## 💬 协作要求

- 与**API CLI**协作: 确认API数据需求
- 与**main**协作: 报告性能指标
- 监控数据库健康状态，及时发现问题

---

**最后更新**: 2026-01-01 20:55
**分配者**: Main CLI
