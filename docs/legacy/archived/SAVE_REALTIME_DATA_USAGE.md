# save_realtime_data.py 完善版使用说明

**Note**: MySQL has been removed; use PostgreSQL. This legacy guide is kept for reference.

## 概述

基于mystocks项目的db_manager工作原理，完善后的`save_realtime_data.py`提供了完整的股票实时数据保存解决方案。

## 主要改进

### 1. **完整的面向对象设计**
- `RealtimeDataSaver`类封装了所有数据保存逻辑
- 支持资源管理和错误处理
- 提供灵活的配置选项

### 2. **增强的数据处理流程**
- 数据验证和清理
- 自动数据类型映射
- 智能表结构生成
- 批量数据插入

### 3. **多种数据更新模式**
- `replace`: 替换重复数据
- `append`: 追加新数据
- `ignore`: 忽略重复数据

### 4. **完善的错误处理机制**
- 自动重试机制（指数退避）
- 详细的日志记录
- 资源自动清理

### 5. **支持定时任务**
- 连续数据采集模式
- 可配置的采集间隔
- 优雅的停止机制

## 使用方法

### 基本使用

```python
from save_realtime_data import save_realtime_data_to_db
from db_manager.database_manager import DatabaseType

# 单次保存数据
success = save_realtime_data_to_db(
    market_symbol='hs',           # 市场代码
    database_type=DatabaseType.POSTGRESQL,
    database_name='stock_db',
    table_name='realtime_quotes',
    update_mode='replace'         # 更新模式
)
```

### 面向对象使用

```python
from save_realtime_data import RealtimeDataSaver
from db_manager.database_manager import DatabaseType

# 创建保存器实例
saver = RealtimeDataSaver(
    database_type=DatabaseType.POSTGRESQL,
    database_name='stock_db',
    table_name='realtime_quotes',
    update_mode='append'
)

try:
    # 保存实时数据
    success = saver.save_realtime_data('hs')
    if success:
        print("数据保存成功")
finally:
    saver.cleanup()  # 清理资源
```

### 连续数据采集

```python
from save_realtime_data import save_realtime_data_continuous

# 每5分钟采集一次数据
save_realtime_data_continuous(
    market_symbol='hs',
    interval_minutes=5,
    database_type=DatabaseType.POSTGRESQL,
    database_name='stock_db',
    table_name='realtime_quotes'
)
```

### 命令行使用

```bash
# 单次执行
python save_realtime_data.py --market hs --db_name stock_db --table realtime_data

# 连续模式（每10分钟采集一次）
python save_realtime_data.py --market hs --continuous --interval 10

# 指定更新模式
python save_realtime_data.py --market hs --mode replace

# 使用其他数据库类型
python save_realtime_data.py --market hs --db_type PostgreSQL
```

## 配置说明

### 数据库配置

确保在`.env`文件中配置数据库连接信息：

```
# PostgreSQL配置
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_PORT=5432

# 监控数据库URL
MONITOR_DB_URL=postgresql://user:password@localhost/db_monitor
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| market_symbol | str | 'hs' | 市场代码（hs=沪深，sh=上海，sz=深圳） |
| database_type | DatabaseType | POSTGRESQL | 数据库类型 |
| database_name | str | 'test_db' | 数据库名称 |
| table_name | str | 'stock_realtime_data' | 表名 |
| update_mode | str | 'replace' | 更新模式（replace/append/ignore） |

## 工作流程

### 1. 数据获取阶段
- 通过CustomerDataSource获取实时数据
- 支持多种数据源（efinance, easyquotation）
- 自动重试机制

### 2. 数据验证阶段
- 检查DataFrame有效性
- 验证必要字段存在
- 数据类型校验

### 3. 数据准备阶段
- 添加时间戳字段
- 处理空值和特殊字符
- 标准化列名

### 4. 表结构管理
- 自动检查表是否存在
- 根据数据自动生成表结构
- 支持表结构演进

### 5. 数据插入阶段
- 批量插入提高性能
- 支持不同更新策略
- 事务处理保证一致性

### 6. 日志和监控
- 详细的操作日志
- 错误信息记录
- 性能指标统计

## 错误处理

### 常见错误及解决方案

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接配置
   - 检查网络连接

2. **数据获取失败**
   - 检查网络连接
   - 验证市场代码
   - 查看customer_adapter状态

3. **表创建失败**
   - 检查数据库权限
   - 验证表名规范
   - 查看DDL生成日志

4. **数据插入失败**
   - 检查数据类型匹配
   - 验证约束条件
   - 查看批量插入日志

## 监控和维护

### 日志文件
- `realtime_data_save.log`: 主要操作日志
- `financial_adapter.log`: 数据源操作日志

### 数据库监控表
- `table_creation_log`: 表创建记录
- `table_operation_log`: 表操作记录
- `table_validation_log`: 表验证记录

### 性能优化建议
1. 适当调整批量插入大小（BATCH_SIZE）
2. 定期清理历史日志
3. 监控数据库连接池状态
4. 定期备份重要数据

## 测试和验证

运行测试脚本验证功能：

```bash
python test_save_realtime_data.py
```

测试内容包括：
- 基本数据保存功能
- 不同更新模式
- 错误处理机制
- 数据验证流程

## 注意事项

1. **数据源依赖**: 确保efinance或easyquotation库已正确安装
2. **数据库权限**: 确保有创建表和插入数据的权限
3. **网络稳定性**: 实时数据获取需要稳定的网络连接
4. **存储空间**: 定期监控数据库存储空间使用情况
5. **并发控制**: 避免多个进程同时写入同一张表

## 扩展建议

1. **数据清理**: 定期清理过期数据
2. **数据分区**: 对于大量历史数据，考虑表分区
3. **缓存机制**: 添加Redis缓存提高查询性能
4. **告警机制**: 集成告警系统监控数据采集状态
5. **API接口**: 提供REST API供其他应用调用
