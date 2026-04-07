# 数据备份恢复系统用户指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


## 📋 目录

1. [概述](#概述)
2. [系统设计](#系统设计)
3. [备份策略](#备份策略)
4. [恢复过程](#恢复过程)
5. [API 文档](#api-文档)
6. [命令行工具](#命令行工具)
7. [监控和维护](#监控和维护)
8. [故障排查](#故障排查)

---

## 概述

MyStocks 备份恢复系统提供完整的数据保护方案，支持：

- **TDengine**: 日全量备份 + 小时增量备份 (RTO: 10分钟, RPO: 1小时)
- **PostgreSQL**: 日全量备份 + WAL 连续归档 (RTO: 5分钟, RPO: 5分钟)
- **数据完整性**: 自动校验和验证
- **自动化调度**: 后台定时备份任务
- **点对点恢复**: 支持任意时刻恢复 (PITR)

---

## 系统设计

### 架构概述

```
┌─────────────────────────────────────────────────────────┐
│         MyStocks Backup & Recovery System               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  BackupManager   │  │ RecoveryManager  │            │
│  │  - Full backup   │  │ - Full restore   │            │
│  │  - Incremental   │  │ - PITR restore   │            │
│  │  - Compression   │  │ - Table restore  │            │
│  └──────────────────┘  └──────────────────┘            │
│          │                      │                       │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │BackupScheduler   │  │IntegrityChecker  │            │
│  │- Hourly backups  │  │ - Hash verify    │            │
│  │- Daily cleanups  │  │ - Row count      │            │
│  │- APScheduler     │  │ - Data validation│            │
│  └──────────────────┘  └──────────────────┘            │
│          │                      │                       │
│  ┌───────────────────────────────────────┐             │
│  │      Backup Storage                   │             │
│  │  - ./backups/tdengine/                │             │
│  │  - ./backups/postgresql/              │             │
│  │  - ./backups/metadata/                │             │
│  │  - ./backups/recovery_logs/           │             │
│  └───────────────────────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 关键组件

#### 1. BackupManager (备份管理器)

**责任**:
- 执行全量和增量备份
- 管理备份文件和元数据
- 压缩和存储备份数据
- 清理过期备份

**文件**: `src/backup_recovery/backup_manager.py`

#### 2. RecoveryManager (恢复管理器)

**责任**:
- 从备份恢复数据
- 实现点对点时间恢复 (PITR)
- 支持表级别恢复
- 记录恢复日志

**文件**: `src/backup_recovery/recovery_manager.py`

#### 3. BackupScheduler (备份调度器)

**责任**:
- 定时执行备份任务
- 管理备份时间表
- 清理过期备份

**文件**: `src/backup_recovery/backup_scheduler.py`

**调度时间表**:
```
02:00 - TDengine 全量备份 (daily)
03:00 - PostgreSQL 全量备份 (daily)
04:00 - 清理过期备份 (daily)
xx:00 - TDengine 增量备份 (hourly, except 02:00)
```

#### 4. IntegrityChecker (完整性检查器)

**责任**:
- 验证备份文件完整性
- 检查恢复数据一致性
- 生成验证报告

**文件**: `src/backup_recovery/integrity_checker.py`

---

## 备份策略

### TDengine 备份策略

#### 全量备份

**时间**: 每天 02:00
**覆盖**: 所有表 (tick_data, minute_kline, order_book_depth, level2_snapshot, index_intraday_quotes)
**格式**: Parquet + gzip 压缩
**目标**:
- RTO: 10 分钟
- RPO: 1 小时

**步骤**:
```python
from src.backup_recovery import BackupManager

backup_mgr = BackupManager()
metadata = backup_mgr.backup_tdengine_full()
print(f"Backup ID: {metadata.backup_id}")
print(f"Size: {metadata.backup_size_bytes / 1024 / 1024:.2f} MB")
```

#### 增量备份

**时间**: 每小时整点（除了 02:00）
**覆盖**: 自上次备份以来的新增/修改数据
**基础**: 上次全量备份
**步骤**:
```python
backup_mgr = BackupManager()
latest_full = backup_mgr.get_latest_backup('tdengine', 'full')
metadata = backup_mgr.backup_tdengine_incremental(latest_full.backup_id)
```

### PostgreSQL 备份策略

#### 全量备份

**时间**: 每天 03:00
**工具**: pg_dump
**格式**: SQL 文本 + gzip 压缩
**目标**:
- RTO: 5 分钟
- RPO: 5 分钟（结合 WAL 归档）

**步骤**:
```python
backup_mgr = BackupManager()
metadata = backup_mgr.backup_postgresql_full()
```

#### WAL 归档配置

PostgreSQL 需要配置 WAL 归档实现连续恢复能力。

**配置步骤**:
```bash
# 1. 创建 WAL 归档目录
mkdir -p /var/lib/postgresql/wal_archive

# 2. 更新 postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 300

# 3. 重启 PostgreSQL
systemctl restart postgresql
```

---

## 恢复过程

### 全量恢复

#### TDengine 全量恢复

```python
from src.backup_recovery import RecoveryManager

recovery_mgr = RecoveryManager()

# 查找最新的全量备份
# 然后恢复
success, message = recovery_mgr.restore_tdengine_from_full_backup(
    backup_id='tdengine_full_20251111_020000',
    target_tables=None,  # None 表示全部表
    dry_run=False,
)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

#### PostgreSQL 全量恢复

```python
success, message = recovery_mgr.restore_postgresql_from_full_backup(
    backup_id='postgresql_full_20251111_030000',
    dry_run=False,
)
```

### 点对点时间恢复 (PITR)

恢复到指定时刻的数据状态。

```python
from datetime import datetime

recovery_mgr = RecoveryManager()

# 恢复到 2 小时前的状态
target_time = datetime.now() - timedelta(hours=2)

success, message = recovery_mgr.restore_tdengine_point_in_time(
    target_time=target_time,
    target_tables=None,
)
```

**PITR 工作流**:
1. 查找不晚于目标时间的最近全量备份
2. 恢复全量备份
3. 应用所有后续增量备份直到目标时间

---

## API 文档

### 备份 API

#### POST /api/backup-recovery/backup/tdengine/full
执行 TDengine 全量备份

**响应**:
```json
{
  "success": true,
  "backup_id": "tdengine_full_20251111_020000",
  "database": "tdengine",
  "backup_type": "full",
  "tables_backed_up": ["tick_data", "minute_kline"],
  "total_rows": 1000000,
  "backup_size_mb": 256.5,
  "compression_ratio": 2.5
}
```

#### POST /api/backup-recovery/backup/postgresql/full
执行 PostgreSQL 全量备份

#### POST /api/backup-recovery/backup/tdengine/incremental
执行 TDengine 增量备份

**参数**:
- `since_backup_id`: 上次备份的 ID

### 恢复 API

#### POST /api/backup-recovery/recovery/tdengine/full
从全量备份恢复 TDengine

**参数**:
- `backup_id`: 备份 ID
- `target_tables`: 指定表列表（可选）
- `dry_run`: 测试运行（可选）

#### POST /api/backup-recovery/recovery/tdengine/pitr
点对点时间恢复

**参数**:
- `target_time`: ISO 8601 格式时间
- `target_tables`: 指定表列表（可选）

### 查询 API

#### GET /api/backup-recovery/backups
列出所有备份

**查询参数**:
- `database`: 数据库类型 (tdengine/postgresql)
- `backup_type`: 备份类型 (full/incremental)
- `status`: 备份状态 (success/failed)

**响应**:
```json
{
  "total": 5,
  "backups": [
    {
      "backup_id": "tdengine_full_20251111_020000",
      "backup_type": "full",
      "database": "tdengine",
      "status": "success",
      "backup_size_mb": 256.5,
      "compression_ratio": 2.5,
      "total_rows": 1000000
    }
  ]
}
```

#### GET /api/backup-recovery/recovery/objectives
获取恢复目标 (RTO/RPO)

#### GET /api/backup-recovery/scheduler/jobs
获取计划的备份任务

---

## 命令行工具

### 安装和使用

```bash
cd /opt/claude/mystocks_spec
chmod +x scripts/runtime/backup_recovery_cli.py
```

### 常用命令

#### 执行备份

```bash
# TDengine 全量备份
python scripts/runtime/backup_recovery_cli.py backup tdengine full

# PostgreSQL 全量备份
python scripts/runtime/backup_recovery_cli.py backup postgresql full

# TDengine 增量备份
python scripts/runtime/backup_recovery_cli.py backup tdengine incremental \
  --since tdengine_full_20251111_020000
```

#### 列出备份

```bash
# 列出所有备份
python scripts/runtime/backup_recovery_cli.py list backups
```

#### 恢复数据

```bash
# 全量恢复
python scripts/runtime/backup_recovery_cli.py restore tdengine full \
  --backup-id tdengine_full_20251111_020000

# PITR 恢复（恢复到 2 小时前）
python scripts/runtime/backup_recovery_cli.py restore tdengine pitr \
  --target-time "2025-11-11T18:00:00"

# 测试运行（不修改数据库）
python scripts/runtime/backup_recovery_cli.py restore tdengine full \
  --backup-id tdengine_full_20251111_020000 \
  --dry-run
```

#### 验证完整性

```bash
python scripts/runtime/backup_recovery_cli.py verify \
  tdengine_full_20251111_020000
```

#### 管理调度

```bash
# 启动备份调度
python scripts/runtime/backup_recovery_cli.py scheduler start

# 查看调度状态
python scripts/runtime/backup_recovery_cli.py scheduler status

# 停止备份调度
python scripts/runtime/backup_recovery_cli.py scheduler stop
```

---

## 监控和维护

### 备份验证

自动验证备份完整性：

```python
from src.backup_recovery import IntegrityChecker

checker = IntegrityChecker()

# 验证备份文件
is_valid, message = checker.verify_backup_integrity(
    backup_file_path,
    expected_checksum='abc123...'
)

# 验证恢复后的数据
is_valid, details = checker.verify_tdengine_recovery(
    backup_metadata,
    expected_row_count=1000000
)

# 生成报告
report_file = checker.generate_integrity_report(
    backup_id,
    {'is_valid': is_valid, 'details': details}
)
```

### 备份清理

自动清理过期备份（保留期默认 30 天）：

```bash
python scripts/runtime/backup_recovery_cli.py cleanup old-backups \
  --retention-days 30
```

或通过 API：

```
POST /api/backup-recovery/cleanup/old-backups?retention_days=30
```

### 监控指标

关键监控指标：
- 备份大小和压缩率
- 备份持续时间
- 备份成功率
- 恢复时间
- 数据行数一致性

---

## 故障排查

### 常见问题

#### 问题: 备份失败

**症状**: `BackupManager.backup_tdengine_full()` 返回失败状态

**排查步骤**:
1. 检查数据库连接是否正常
2. 查看日志中的错误信息
3. 验证备份目录的写入权限

```bash
# 检查权限
ls -la ./backups/

# 检查磁盘空间
df -h
```

#### 问题: 恢复失败

**症状**: 恢复过程出错

**排查步骤**:
1. 验证备份文件完整性
2. 检查备份格式和压缩状态
3. 确保目标数据库可写

```python
# 验证备份完整性
is_valid, details = integrity_checker.verify_tdengine_recovery(
    metadata,
    expected_row_count
)

# 查看恢复日志
with open('./backups/recovery_logs/recovery_*.log', 'r') as f:
    print(f.read())
```

#### 问题: PITR 失败

**症状**: 无法恢复到指定时刻

**排查步骤**:
1. 检查是否有足够的增量备份
2. 验证目标时间是否有备份覆盖
3. 检查备份元数据的时间戳

```python
# 列出所有备份，确认时间覆盖
backups = backup_manager.get_backup_list()
for b in backups:
    print(f"{b.backup_id}: {b.start_time} ~ {b.end_time}")
```

### 日志位置

```
./backups/
├── metadata/              # 备份元数据 (JSON)
├── recovery_logs/         # 恢复日志
├── tdengine/             # TDengine 备份文件
└── postgresql/           # PostgreSQL 备份文件
```

---

## 性能优化建议

1. **调整备份时间**: 避免业务高峰期
2. **启用压缩**: 减少存储空间和网络传输
3. **增量备份**: 减少备份时间和存储
4. **并行恢复**: 大型数据集使用表级并行恢复
5. **外部存储**: 将备份文件定期转移到外部存储（云存储）

---

## 参考资源

- [TDengine 官方文档](https://docs.taosdata.com/)
- [PostgreSQL 备份文档](https://www.postgresql.org/docs/current/backup.html)
- [APScheduler 文档](https://apscheduler.readthedocs.io/)

---

**最后更新**: 2025-11-11
**版本**: 1.0.0
