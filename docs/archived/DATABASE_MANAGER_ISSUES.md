# DatabaseTableManager 问题记录

**日期**: 2025-10-24
**发现者**: Claude (Day 5 Validation)
**优先级**: P0 (阻塞 100% 架构合规)

---

## 问题摘要

`DatabaseTableManager.batch_create_tables()` 在创建 Web 层表时遇到 2 个关键问题，导致仅创建了 4/6 张表。

**影响**：
- ❌ 违背 ConfigDrivenTableManager 架构原则
- ❌ 无法达到 100% 架构合规
- ❌ backtest_trades 和 risk_alerts 表未创建

---

## 问题 #1: PostgreSQL ENUM 缺少 name 参数 ✅ **已修复**

### 错误信息
```
sqlalchemy.exc.CompileError: PostgreSQL ENUM type requires a name.
```

### 根本原因
`db_manager/database_manager.py` 第 118-120 行：
```python
# ❌ 错误写法
operation_type = Column(SQLEnum('CREATE', 'ALTER', 'DROP', 'VALIDATE'), nullable=False)
operation_status = Column(SQLEnum('success', 'failed', 'processing'), nullable=False)
```

PostgreSQL 要求所有 ENUM 类型必须有 `name` 参数。

### 修复方案
```python
# ✅ 正确写法
operation_type = Column(SQLEnum('CREATE', 'ALTER', 'DROP', 'VALIDATE', name='operation_type_enum'), nullable=False)
operation_status = Column(SQLEnum('success', 'failed', 'processing', name='operation_status_enum'), nullable=False)
```

### 状态
✅ **已于 2025-10-24 修复**

---

## 问题 #2: default_value 字段类型转换错误 ⚠️ **待修复**

### 错误信息
```
ERROR:DatabaseTableManager:Failed to create table backtests:
(psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type numeric: "'pending'"
LINE 1: ...status', 'VARCHAR', 20, NULL, NULL, false, false, '''pending...
```

### 根本原因

**监控数据库表定义** (`column_definition_log` 表)：
```python
class ColumnDefinitionLog(Base):
    __tablename__ = 'column_definition_log'

    id = Column(Integer, primary_key=True)
    table_log_id = Column(Integer, sa.ForeignKey('table_creation_log.id'))
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    col_length = Column(Integer)
    col_precision = Column(Integer)
    col_scale = Column(Integer)
    is_nullable = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    default_value = Column(String(255))  # ⚠️ 这里是 String 类型
    comment = Column(Text)
```

**问题发生时的数据**：
- `default_value = "'pending'"` (字符串，包含引号)
- `col_length = 20` (INTEGER 类型)
- `col_precision = None` (INTEGER 类型)
- `col_scale = None` (INTEGER 类型)

**SQLAlchemy 错误行为**：
在批量插入时，SQLAlchemy 尝试将 `default_value` 的值 `"'pending'"` 转换为 NUMERIC 类型，而不是 String 类型。

**可能的原因**：
1. 批量插入时的类型推断错误
2. 参数绑定时的类型转换问题
3. 监控数据库（PostgreSQL）的严格类型检查

### 影响范围

**未创建的表**：
- `backtest_trades` (6.4)
- `risk_alerts` (6.6)

**已创建的表**：
- ✅ `strategies` (6.1)
- ✅ `models` (6.2)
- ✅ `backtests` (6.3) - 部分字段有问题，但表结构已创建
- ✅ `risk_metrics` (6.5)

### 修复策略

#### 方案 A: 修复 DatabaseTableManager 的类型处理逻辑 ✅ **推荐**

**文件**: `/opt/claude/mystocks_spec/db_manager/database_manager.py`

**需要修改的方法**：
- `_create_postgresql_table()`
- `batch_create_tables()`

**具体修复**：
1. 在记录列定义到监控数据库前，显式转换 `default_value` 为字符串
2. 确保所有 None 值正确处理
3. 分离表创建逻辑和监控日志记录逻辑

#### 方案 B: 简化监控日志记录

如果问题复杂，可以：
1. 先创建业务表（PostgreSQL）
2. 后记录监控日志（使用 try-except 包裹）
3. 确保业务表创建不受监控日志影响

### 临时解决方案（Week 2 前）

**Day 5 验证任务**：
1. 删除所有已创建的表
2. 修复 DatabaseTableManager 代码
3. 重新运行 `batch_create_tables()`
4. 验证所有 6 张表创建成功

**禁止操作**：
- ❌ 不得用 SQL 直接创建表绕过 ConfigDrivenTableManager
- ❌ 不得修改 table_config.yaml 以规避问题
- ❌ 不得降低架构合规标准

---

## 问题 #3: 其他数据库连接失败（非阻塞）

### 错误信息
```
ERROR:DatabaseTableManager:Failed to connect to TDengine database market_data: Connection refused
ERROR:DatabaseTableManager:Failed to connect to MySQL database mystocks_reference: Access denied
```

### 根本原因
Week 3 简化架构后，TDengine 和 MySQL 已不再使用，但 `table_config.yaml` 中仍包含这些表的定义。

### 修复策略
- Week 2 任务：清理 table_config.yaml 中不再使用的表定义
- 或：修改 DatabaseTableManager 使其跳过不可用的数据库

### 优先级
P2 (不影响 Web 层表创建)

---

## 下一步行动

### Day 5 立即修复（P0）
1. ✅ 修复 ENUM name 问题
2. ⏳ 修复 default_value 类型转换问题
3. ⏳ 删除所有表并重新通过 ConfigDrivenTableManager 创建
4. ⏳ 验证所有 6 张表创建成功

### Week 2 优化（P1）
1. 清理 table_config.yaml 中不再使用的 TDengine/MySQL 表定义
2. 增强 DatabaseTableManager 的错误处理
3. 分离业务表创建和监控日志记录逻辑

---

## 架构合规原则

**核心要求**：
1. ✅ 所有表定义在 `table_config.yaml` 中
2. ✅ 所有表通过 `ConfigDrivenTableManager.batch_create_tables()` 创建
3. ❌ **严禁**使用独立 SQL 脚本绕过架构模式
4. ❌ **严禁**临时补救措施违背架构原则

**目标**：
- 100% 架构合规
- 所有表通过配置驱动自动化创建
- 可审计、可追溯、可重复

---

**记录人**: Claude
**最后更新**: 2025-10-24
**状态**: 问题 #1 已修复 | 问题 #2 待修复 | 问题 #3 Week 2 处理
