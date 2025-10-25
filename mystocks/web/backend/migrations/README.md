# Web Backend Database Migrations

## ⚠️ Important Note

**The web application tables are now managed through `table_config.yaml`** following the project's ConfigDrivenTableManager pattern.

## Table Definitions Location

All web table definitions are located in:
```
/opt/claude/mystocks_spec/config/table_config.yaml
```

Under section "第6类: Web应用层表 (Web Application)"

## Tables Managed

The following 6 tables are defined in `table_config.yaml`:

1. **strategies** - 交易策略表
2. **models** - 机器学习模型表
3. **backtests** - 回测任务表
4. **backtest_trades** - 回测交易明细表
5. **risk_metrics** - 风险指标表
6. **risk_alerts** - 风险预警规则表

## Creating Tables

To create these tables, use the ConfigDrivenTableManager:

```python
from db_manager.database_manager import DatabaseTableManager

mgr = DatabaseTableManager()
mgr.batch_create_tables('/opt/claude/mystocks_spec/config/table_config.yaml')
```

Or use the MyStocksUnifiedManager for full system initialization:

```python
from unified_manager import MyStocksUnifiedManager

manager = MyStocksUnifiedManager()
manager.initialize_system()
```

## Architecture Compliance

✅ **ConfigDrivenTableManager**: All tables defined in YAML config
✅ **Single Database**: All tables in PostgreSQL (mystocks database)
✅ **Single-User System**: No user_id columns
✅ **Monitoring Integration**: MonitoringDatabase tracks all operations

## Legacy Migration File

The file `001_create_web_tables.sql` is deprecated and should not be used.
It has been replaced by the table definitions in `table_config.yaml`.
