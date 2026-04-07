# User Story 2 进度报告: 简化数据库架构（代码级）

> **历史总结说明**:
> 本文件是某次测试执行、阶段交付、修复验收或专题推进的历史总结快照，用于追溯当时的实施结论。
> 其中的完成度、通过数、结论和结果不应直接视为当前事实；引用前应结合 `architecture/STANDARDS.md`、当前测试实现与最新验证结果重新确认。


**报告时间**: 2025-10-25
**状态**: 🔄 进行中 (约40%完成)
**分支**: 002-arch-optimization

---

## 执行摘要

User Story 2旨在从代码层面完全移除MySQL和Redis，简化为仅使用TDengine和PostgreSQL的双数据库架构。

### 当前进度

- **已完成**: 7/17 任务 (41%)
- **进行中**: 1/17 任务 (6%)
- **待完成**: 9/17 任务 (53%)

---

## 已完成任务 ✅

### T025-T028: 数据迁移任务 (Week 3已完成)

**状态**: ✅ 100% 完成

这些任务在Week 3架构简化时已经完成：
- ✅ T025: MySQL到PostgreSQL迁移脚本已创建 (`scripts/migrate_mysql_to_postgresql.py`)
- ✅ T026: Dry-run验证已执行
- ✅ T027: 实际数据迁移已完成（18表，299行数据）
- ✅ T028: PostgreSQL数据完整性已验证

**证据**:
- README.md中记录："MySQL已移除：所有参考数据和元数据已迁移至PostgreSQL（299行数据）"
- 迁移脚本存在于`scripts/migrate_mysql_to_postgresql.py`

### T029: 从core.py移除MySQL路由逻辑 ✅

**状态**: ✅ 100% 完成

**完成内容**:

1. **DatabaseTarget枚举简化**:
   ```python
   # 修改前
   class DatabaseTarget(Enum):
       TDENGINE = "TDengine"
       POSTGRESQL = "PostgreSQL"
       REDIS = "Redis"
       MYSQL = "MySQL"
       MARIADB = "MariaDB"

   # 修改后
   class DatabaseTarget(Enum):
       """目标数据库类型 - 基于数据特性选择 (Week 3简化后)"""
       TDENGINE = "TDengine"          # 高频时序数据专用
       POSTGRESQL = "PostgreSQL"      # 通用数据仓库+TimescaleDB时序扩展
   ```

2. **DataClassification注释更新**:
   - 第2类（参考数据）: MySQL/MariaDB → PostgreSQL
   - 第4类（交易数据）: Redis（热数据） → PostgreSQL（应用层缓存）
   - 第5类（元数据）: MySQL/MariaDB → PostgreSQL

3. **CLASSIFICATION_TO_DATABASE映射更新**:
   - 所有分类全部映射到TDengine或PostgreSQL
   - 移除了所有MySQL和Redis目标

4. **get_target_database默认值**:
   ```python
   # 修改后
   return cls.CLASSIFICATION_TO_DATABASE.get(classification, DatabaseTarget.POSTGRESQL)
   ```

5. **get_database_name简化**:
   ```python
   # 修改后 - 仅2个数据库
   if target_db == DatabaseTarget.TDENGINE:
       return "market_data"
   else:  # DatabaseTarget.POSTGRESQL
       return "mystocks"
   ```

6. **配置模板databases块**:
   ```python
   # 移除了mysql和redis配置块
   'databases': {
       'tdengine': {...},
       'postgresql': {...}
   }
   ```

7. **示例表定义更新**:
   ```python
   # symbols表和trade_calendar表
   'database_type': 'PostgreSQL',  # 从MySQL改为PostgreSQL
   'database_name': 'mystocks',    # 从quant_research改为mystocks
   ```

8. **类型转换逻辑**:
   ```python
   # 添加了明确的错误提示
   elif db_type_str in ['MySQL', 'MariaDB', 'Redis']:
       logger.error(f"数据库类型 '{db_type_str}' 已在Week 3架构简化中移除，请使用PostgreSQL")
       return False
   ```

**文件变更**:
- `core.py`: 9处关键修改
- 行数影响: ~50行删除/修改

### T032: 从core.py移除Redis路由逻辑 ✅

**状态**: ✅ 100% 完成

Redis路由逻辑已与T029一同完成，包括：
- DatabaseTarget枚举中移除REDIS
- 数据分类注释中将Redis改为PostgreSQL
- CLASSIFICATION_TO_DATABASE中移除Redis映射
- 配置模板中移除redis块

---

## 进行中任务 🔄

### T030: 从unified_manager.py移除MySQL连接

**状态**: 🔄 进行中 (0% - 已识别范围)

**发现的MySQL/Redis引用** (unified_manager.py):

1. **Import语句** (第36-37行):
   ```python
   MySQLDataAccess,
   RedisDataAccess
   ```

2. **实例化** (第88-89行):
   ```python
   self.mysql = MySQLDataAccess()
   self.redis = RedisDataAccess()
   ```

3. **save_data_by_classification** (第191-199行):
   ```python
   rows_affected = self.mysql.insert_dataframe(table_name, data)
   print(f"✅ MySQL保存成功: {rows_affected}行")

   # Redis使用特殊逻辑
   ttl = kwargs.get('ttl') or DataStorageRules.get_redis_ttl(classification)
   self._save_to_redis(table_name, data, ttl)
   print(f"✅ Redis保存成功: {rows_affected}条记录")
   ```

4. **load_data_by_classification** (第337-342行):
   ```python
   # MySQL查询
   df = self.mysql.query(table_name, columns, where, limit=limit)

   # Redis查询
   df = self._load_from_redis(table_name, filters)
   ```

5. **辅助方法**:
   - `_save_to_redis()` 方法
   - `_load_from_redis()` 方法

**待执行操作**:
- [ ] 移除MySQLDataAccess和RedisDataAccess导入
- [ ] 移除self.mysql和self.redis实例化
- [ ] 删除save_data_by_classification中的MySQL/Redis分支
- [ ] 删除load_data_by_classification中的MySQL/Redis分支
- [ ] 删除_save_to_redis和_load_from_redis方法
- [ ] 更新相关文档字符串

**预计工作量**: 中等 (~30-40分钟)

---

## 待完成任务 ⏳

### 代码清理任务

#### T031: 从data_access.py删除MySQLDataAccess类

**状态**: ⏳ 待开始

**需要删除**:
- MySQLDataAccess类完整定义
- 相关MySQL导入（pymysql等）
- MySQL特定的辅助方法

**预计工作量**: 中等 (~20-30分钟)

#### T033: 从unified_manager.py移除Redis连接

**状态**: ⏳ 待开始 (将与T030合并执行)

这个任务会与T030一起完成，因为它们在同一文件中。

#### T034: 从data_access.py删除RedisDataAccess类

**状态**: ⏳ 待开始

**需要删除**:
- RedisDataAccess类完整定义
- 相关Redis导入（redis库等）
- Redis特定的辅助方法

**预计工作量**: 中等 (~20-30分钟)

#### T035: 更新requirements.txt移除pymysql和redis

**状态**: ⏳ 待开始

**需要移除的依赖**:
- pymysql
- PyMySQL
- redis
- 其他MySQL/Redis相关库

**预计工作量**: 小 (~5-10分钟)

#### T036: 更新监控数据库为PostgreSQL

**状态**: ⏳ 待开始

**需要修改的文件**:
- `monitoring/monitoring_database.py`
- 可能需要更新的：`monitoring/performance_monitor.py`
- 可能需要更新的：`monitoring/data_quality_monitor.py`

**需要执行**:
- 检查当前监控数据库配置
- 确认是否已经使用PostgreSQL
- 移除任何MySQL/Redis监控逻辑

**预计工作量**: 中等 (~30-40分钟)

#### T037: 运行系统初始化测试

**状态**: ⏳ 待开始

**测试内容**:
```bash
python -c "from unified_manager import MyStocksUnifiedManager; mgr = MyStocksUnifiedManager(); mgr.initialize_system()"
```

**验证目标**:
- 系统仅连接TDengine和PostgreSQL
- 无MySQL/Redis连接尝试
- 所有表成功创建
- 无错误或警告

**预计工作量**: 小 (~10-15分钟) + 调试时间

### Web集成任务

#### T038: 创建数据库监控仪表板页面

**状态**: ⏳ 待开始

**文件**: `web/frontend/src/views/system/DatabaseMonitor.vue`

**功能需求**:
- 显示TDengine和PostgreSQL状态
- 连接池统计
- 查询性能指标
- 存储空间使用
- 实时健康状态

**预计工作量**: 大 (~60-90分钟)

#### T039: 实现数据库健康检查API

**状态**: ⏳ 待开始

**文件**: `web/backend/app/api/system.py`

**端点**: `GET /api/system/database/health`

**返回数据**:
```json
{
  "tdengine": {
    "status": "healthy",
    "version": "3.3.6.13",
    "connection": "active",
    "database": "market_data"
  },
  "postgresql": {
    "status": "healthy",
    "version": "17.6",
    "connection": "active",
    "database": "mystocks"
  }
}
```

**预计工作量**: 中等 (~30-40分钟)

#### T040: 实现数据库连接池统计API

**状态**: ⏳ 待开始

**文件**: `web/backend/app/api/system.py`

**端点**: `GET /api/system/database/pool-stats`

**返回数据**:
```json
{
  "tdengine": {
    "pool_size": 10,
    "active_connections": 3,
    "idle_connections": 7
  },
  "postgresql": {
    "pool_size": 20,
    "active_connections": 5,
    "idle_connections": 15
  }
}
```

**预计工作量**: 中等 (~30-40分钟)

#### T041: 添加数据库监控菜单

**状态**: ⏳ 待开始

**文件**:
- `web/frontend/src/config/menu.config.js`
- `web/frontend/src/router/index.js`

**需要添加**:
- 菜单项：系统管理 → 数据库监控
- 路由：/system/database-monitor

**预计工作量**: 小 (~10-15分钟)

---

## 风险和障碍

### 潜在风险

1. **代码依赖复杂性**:
   - unified_manager.py和data_access.py可能有未发现的MySQL/Redis依赖
   - 需要全面测试以确保无遗漏

2. **测试覆盖不足**:
   - T037系统初始化测试可能暴露新问题
   - 需要充分的回归测试

3. **监控数据库状态未知**:
   - T036需要先检查当前监控数据库的实际配置
   - 可能需要数据迁移

### 缓解措施

1. **系统性代码审查**:
   - 使用grep全局搜索所有MySQL/Redis引用
   - 逐文件验证清理完整性

2. **分阶段测试**:
   - 每完成一个主要任务就执行测试
   - 使用git提交隔离变更

3. **文档先行**:
   - 更新文档与代码同步
   - 保持CLAUDE.md和README.md一致性

---

## 时间估算

### 剩余工作量估算

| 任务组 | 任务数 | 预计时间 | 优先级 |
|--------|--------|----------|--------|
| 代码清理 | 5 | 2-3小时 | P0 |
| Web集成 | 4 | 3-4小时 | P1 |
| 测试验证 | 1 | 0.5-1小时 | P0 |
| **总计** | **10** | **5.5-8小时** | - |

### 建议执行顺序

**Phase 1: 核心代码清理** (优先级P0)
1. T030 + T033: unified_manager.py清理
2. T031 + T034: data_access.py清理
3. T035: requirements.txt更新
4. T036: 监控数据库更新
5. T037: 系统初始化测试

**Phase 2: Web集成** (优先级P1)
6. T039: 健康检查API
7. T040: 连接池统计API
8. T038: 监控仪表板页面
9. T041: 菜单配置

---

## 下一步行动

### 立即行动

1. **继续T030**: 完成unified_manager.py的MySQL/Redis移除
2. **执行T031**: 删除data_access.py中的MySQLDataAccess类
3. **执行T034**: 删除data_access.py中的RedisDataAccess类

### 中期计划

4. 完成所有代码清理任务（T030-T036）
5. 执行系统初始化测试（T037）
6. 修复测试中发现的问题

### 长期目标

7. 完成Web集成任务（T038-T041）
8. 创建US2完成报告
9. 提交所有变更到Git
10. 准备开始User Story 3

---

## 完成标准

User Story 2将在满足以下条件时视为完成：

### 代码层面
- ✅ core.py中无MySQL/Redis引用
- ⏳ unified_manager.py中无MySQL/Redis引用
- ⏳ data_access.py中无MySQLDataAccess/RedisDataAccess类
- ⏳ requirements.txt中无pymysql/redis依赖
- ⏳ 监控数据库使用PostgreSQL

### 功能层面
- ⏳ 系统初始化仅连接TDengine和PostgreSQL
- ⏳ 所有数据保存/查询操作正常工作
- ⏳ Web监控界面显示2个数据库状态

### 文档层面
- ✅ CLAUDE.md已更新（US1完成）
- ✅ README.md已更新（US1完成）
- ✅ .env.example已更新（US1完成）
- ⏳ 代码注释准确反映架构

---

**报告生成时间**: 2025-10-25 08:55
**下次更新**: 完成T030后
**负责人**: Claude Code
