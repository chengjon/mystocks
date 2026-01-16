# 数据迁移 - Spec Delta

**能力**: 数据迁移 (Data Migration)
**变更ID**: add-smart-quant-monitoring
**状态**: 待审核

---

## ADDED Requirements

### Requirement: 备份现有watchlist数据

The system MUST automatically backup existing watchlist database before migration to ensure data safety.

#### Scenario: 自动备份SQLite数据库

**GIVEN** 现有 watchlist.db 文件位于 `/path/to/watchlist.db`
**WHEN** 管理员执行迁移脚本
**THEN** 系统自动创建备份文件：
  ```
  /backups/watchlist_db_20260107.sqlite
  ```
**AND** 备份文件命名格式：`watchlist_db_YYYYMMDD.sqlite`
**AND** 验证备份文件完整性（校验和匹配）
**AND** 日志记录："✅ 备份文件已创建：/backups/watchlist_db_20260107.sqlite"

#### Scenario: 验证备份文件可恢复

**GIVEN** 系统已创建备份文件
**WHEN** 执行验证脚本
**THEN** 系统测试备份文件：
  - 文件可打开
  - 数据完整性验证通过
  - 表结构完整
**AND** 验证通过后才继续迁移

---

### Requirement: 读取现有watchlist数据

The system MUST read watchlist and stock data from SQLite database and perform integrity validation.

#### Scenario: 读取watchlist主表数据

**GIVEN** SQLite数据库中 `watchlists` 表包含5条记录
**WHEN** 迁移脚本读取数据
**THEN** 系统读取所有字段：
  - id, group_id, name, description
  - created_at, updated_at
**AND** 转换为新数据结构：
  - group_id → watchlist_id
  - name → name
  - description → type (默认 'manual')
**AND** 验证数据：5条记录全部读取成功

#### Scenario: 读取watchlist_stocks表数据

**GIVEN** SQLite数据库中 `watchlist_stocks` 表包含100条记录
**WHEN** 迁移脚本读取数据
**THEN** 系统读取所有字段：
  - id, group_id, stock_code
  - entry_price, entry_at
**AND** 验证数据：
  - 所有 stock_code 格式正确（如 "600519.SH"）
  - entry_price 在合理范围（>0）
  - entry_at 为有效日期
**AND** 100条记录全部读取成功

#### Scenario: 数据完整性检查失败

**GIVEN** SQLite数据库中部分数据损坏
**WHEN** 迁移脚本读取数据
**THEN** 系统检测到异常：
  - stock_code = "INVALID"（格式错误）
  - entry_price = -100（负数）
**AND** 系统记录错误日志
**AND** 迁移终止并提示用户修复数据

---

### Requirement: 批量写入PostgreSQL

The system MUST use async connection pool to batch write data to PostgreSQL for improved migration performance.

#### Scenario: 批量写入清单主表

**GIVEN** 从SQLite读取5条watchlist记录
**WHEN** 迁移脚本执行批量写入
**THEN** 系统使用 `postgres_async` 连接池：
  ```python
  async with postgres_async.pool.acquire() as conn:
      for wl in watchlists:
          watchlist_id = await conn.fetchval(
              """INSERT INTO monitoring_watchlists
                 (user_id, name, type)
                 VALUES ($1, $2, 'manual')
                 RETURNING id
              """, wl['user_id'], wl['name']
          )
  ```
**AND** 5条记录全部写入成功
**AND** 返回新创建的 watchlist_id 列表

#### Scenario: 批量写入清单成员表

**GIVEN** 从SQLite读取100条stock记录
**WHEN** 迁移脚本执行批量写入
**THEN** 系统使用 `executemany` 批量插入：
  ```python
  await conn.executemany(
      """INSERT INTO monitoring_watchlist_stocks
         (watchlist_id, stock_code, entry_price, entry_at)
         VALUES ($1, $2, $3, $4)
      """,
      [(watchlist_id, stock['code'], stock.get('entry_price'),
        stock.get('entry_at', datetime.now()))
       for stock in stocks]
  )
  ```
**AND** 100条记录批量写入 <1秒

#### Scenario: 处理entry_price为NULL的情况

**GIVEN** SQLite中部分记录的 entry_price = NULL
**WHEN** 迁移脚本写入PostgreSQL
**THEN** 系统允许 entry_price 为 NULL
**AND** PostgreSQL字段设置为可空：
  ```sql
  entry_price DECIMAL(10,2) NULL
  ```
**AND** 数据正常写入

---

### Requirement: 验证迁移结果

The system MUST validate data integrity after migration completion to ensure no data loss or corruption.

#### Scenario: 验证记录数量一致性

**GIVEN** 迁移前SQLite数据：
  - watchlists: 5条
  - watchlist_stocks: 100条
**WHEN** 迁移完成后执行验证
**THEN** PostgreSQL数据：
  - monitoring_watchlists: 5条 ✓
  - monitoring_watchlist_stocks: 100条 ✓
**AND** 数量完全匹配

#### Scenario: 验证数据内容一致性

**GIVEN** 迁移前某条记录：
  ```
  stock_code: 600519.SH
  entry_price: 1850.50
  entry_at: 2025-12-01 10:30:00
  ```
**WHEN** 迁移后查询PostgreSQL
**THEN** 新记录内容完全匹配：
  ```
  stock_code: 600519.SH ✓
  entry_price: 1850.50 ✓
  entry_at: 2025-12-01 10:30:00 ✓
  ```
**AND** 数据完整性验证通过

#### Scenario: 验证外键约束

**GIVEN** PostgreSQL数据：
  - monitoring_watchlists: id=1,2,3,4,5
  - monitoring_watchlist_stocks: 100条记录（watchlist_id在1-5之间）
**WHEN** 执行外键约束验证
**THEN** 所有 stocks 的 watchlist_id 都有效
**AND** 无孤立记录
**AND** 外键约束生效

#### Scenario: 检测数据丢失

**GIVEN** 迁移前SQLite有100条记录
**WHEN** 迁移后PostgreSQL只有98条记录
**THEN** 验证脚本检测到数据丢失
**AND** 返回错误：
  ```
  ❌ 数据丢失：预期100条，实际98条
  丢失记录：[stock_code_1, stock_code_2]
  ```
**AND** 提示用户回滚或重新迁移

---

### Requirement: 迁移回滚机制

The system MUST provide rollback mechanism to restore pre-migration state when migration fails.

#### Scenario: 迁移失败时自动回滚

**GIVEN** 迁移过程中发生错误（如：数据库连接断开）
**WHEN** 检测到迁移失败
**THEN** 系统自动执行回滚：
  1. 删除 monitoring_watchlists 表中已插入的数据
  2. 删除 monitoring_watchlist_stocks 表中已插入的数据
  3. 恢复到迁移前状态
**AND** 日志记录："❌ 迁移失败，已回滚所有更改"

#### Scenario: 手动回滚并恢复备份

**GIVEN** 用户发现迁移后数据有问题
**WHEN** 用户执行手动回滚脚本
**THEN** 系统执行：
  1. 清空 monitoring_watchlists 和 monitoring_watchlist_stocks 表
  2. 从备份文件恢复SQLite数据库
**AND** 系统恢复到迁移前状态
**AND** 用户可重新修复数据后再次迁移

---

### Requirement: 管理API接口

The system MUST provide management API endpoints to support remote triggering of data migration and validation.

#### Scenario: 管理员通过API触发迁移

**GIVEN** 管理员拥有管理权限
**WHEN** 管理员发送 POST 请求到 `/api/v1/admin/migrate-watchlists`
**AND** 请求体包含：
```json
{
  "validate_only": false,
  "batch_size": 100
}
```
**THEN** 系统执行完整迁移流程：
  1. 备份现有数据
  2. 读取SQLite数据
  3. 验证数据完整性
  4. 批量写入PostgreSQL
  5. 验证迁移结果
**AND** 返回迁移报告：
```json
{
  "status": "success",
  "watchlists_migrated": 5,
  "stocks_migrated": 100,
  "duration_seconds": 2.5,
  "backup_file": "/backups/watchlist_db_20260107.sqlite"
}
```

#### Scenario: 验证模式迁移（仅验证不执行）

**GIVEN** 管理员想要先验证数据但不执行迁移
**WHEN** 管理员发送 POST 请求到 `/api/v1/admin/migrate-watchlists`
**AND** 请求体包含：
```json
{
  "validate_only": true
}
```
**THEN** 系统仅执行验证步骤：
  1. 读取SQLite数据
  2. 验证数据完整性
  3. 报告潜在问题
**AND** 不执行实际写入
**AND** 返回验证报告：
```json
{
  "status": "validation_passed",
  "issues": [],
  "watchlists_to_migrate": 5,
  "stocks_to_migrate": 100
}
```

#### Scenario: 权限检查

**GIVEN** 普通用户（无管理权限）尝试调用迁移API
**WHEN** 用户发送 POST 请求到 `/api/v1/admin/migrate-watchlists`
**THEN** 系统返回 403 Forbidden
**AND** 错误消息："需要管理员权限"

---

### Requirement: 迁移日志和报告

The system MUST generate detailed migration logs and reports for auditing and troubleshooting.

#### Scenario: 生成迁移报告

**GIVEN** 迁移执行完成
**WHEN** 系统生成迁移报告
**THEN** 报告包含：
  - 迁移开始时间
  - 迁移结束时间
  - 总耗时
  - 成功迁移记录数
  - 失败记录数（如果有）
  - 备份文件路径
  - 验证结果
  - 错误日志（如果有）
**AND** 报告保存到：`docs/reports/MIGRATION_REPORT_YYYYMMDD.json`

#### Scenario: 记录详细操作日志

**GIVEN** 迁移过程执行中
**WHEN** 每个步骤执行
**THEN** 系统记录日志：
  ```
  [2026-01-07 10:00:00] INFO: 开始数据迁移
  [2026-01-07 10:00:01] INFO: 备份文件已创建：/backups/watchlist_db_20260107.sqlite
  [2026-01-07 10:00:02] INFO: 读取watchlist数据：5条记录
  [2026-01-07 10:00:03] INFO: 读取stock数据：100条记录
  [2026-01-07 10:00:05] INFO: 批量写入monitoring_watchlists：5条成功
  [2026-01-07 10:00:06] INFO: 批量写入monitoring_watchlist_stocks：100条成功
  [2026-01-07 10:00:07] INFO: 验证迁移结果：通过
  [2026-01-07 10:00:07] INFO: 迁移完成，总耗时：7秒
  ```

---

## MODIFIED Requirements

*无修改现有需求*

---

## REMOVED Requirements

*无删除现有需求*

---

## Cross-References

- **依赖**: `watchlist-management` - 目标数据结构
- **前置**: 现有 watchlist.db SQLite数据库
- **关联**: Phase 3任务3.4 - 数据迁移脚本

---

## 迁移脚本

### 主迁移脚本

```python
# scripts/migrations/migrate_watchlist_to_monitoring.py

async def migrate_watchlists(
    validate_only: bool = False,
    batch_size: int = 100
):
    """迁移现有监控清单到新系统"""

    # 1. 备份现有数据
    backup_file = await backup_watchlist_db()

    # 2. 读取SQLite数据
    old_watchlists = await read_from_watchlist_db()

    # 3. 验证数据完整性
    validation_result = validate_old_data(old_watchlists)
    if not validation_result.is_valid:
        raise MigrationError(f"数据验证失败: {validation_result.errors}")

    if validate_only:
        return MigrationReport(status="validation_passed", ...)

    # 4. 写入PostgreSQL
    async with postgres_async.pool.acquire() as conn:
        for wl in old_watchlists:
            # 创建主表记录
            watchlist_id = await conn.fetchval(...)

            # 批量插入成员
            await conn.executemary(...)

    # 5. 验证迁移结果
    await validate_migration_results()

    return MigrationReport(status="success", ...)
```

---

## 数据映射

### 字段映射表

| SQLite字段 | PostgreSQL字段 | 转换规则 |
|-----------|---------------|----------|
| group_id | watchlist_id | 直接映射 |
| name | name | 直接映射 |
| description | type | 固定为 'manual' |
| stock_code | stock_code | 直接映射 |
| entry_price | entry_price | 直接映射，允许NULL |
| entry_at | entry_at | 直接映射，默认NOW() |
| NULL | entry_reason | 默认 'migrated' |
| NULL | stop_loss_price | NULL |
| NULL | target_price | NULL |
| NULL | weight | 默认 0.0 |

---

## 性能要求

- 迁移100只股票 <5秒
- 迁移1000只股票 <30秒
- 验证过程 <1秒

---

## 安全要求

- 备份文件权限：600（仅所有者读写）
- 迁移接口需要管理员权限
- 敏感字段加密（可选）

---

**状态**: 待审核
**版本**: v1.0
