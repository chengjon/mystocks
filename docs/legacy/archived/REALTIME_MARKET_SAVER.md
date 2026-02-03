# MyStocks 沪深市场A股实时数据保存系统

**Note**: MySQL has been removed; use PostgreSQL. This legacy guide is kept for reference.

## 快速启动

```bash
# 基础运行
python run_realtime_market_saver.py

# 首次使用（推荐先验证架构）
python run_realtime_market_saver.py --validate

# 使用自定义配置
python run_realtime_market_saver.py --config 自定义配置.env

# 查看帮助
python run_realtime_market_saver.py --help
```

## 系统架构

### 数据分类自动路由

- **实时行情快照** → `REALTIME_POSITIONS` → Redis (热数据，快速访问)
- **Tick时序数据** → `TICK_DATA` → TDengine (时序存储，历史分析)
- **日线数据** → `DAILY_KLINE` → PostgreSQL (分析存储)
- **股票信息** → `SYMBOLS_INFO` → PostgreSQL (参考数据)

### 配置文件

配置文件位置：`db_manager/realtime_market_config.env`

关键配置项：
- `MARKET_SYMBOL=hs` # 'hs'=沪深, 'sh'=上海, 'sz'=深圳
- `SAVE_AS_REALTIME=true` # 保存为实时数据 → Redis
- `SAVE_AS_TICK=false` # 保存为Tick数据 → TDengine

## 文件结构

```
mystocks/
├── run_realtime_market_saver.py          # 统一启动器 (主程序)
├── db_manager/                            # 数据库管理目录
│   ├── save_realtime_market_data.py      # 实时数据保存器
│   ├── realtime_market_config.env        # 配置文件
│   └── validate_mystocks_architecture.py # 架构验证
├── unified_manager.py                     # 统一管理器
├── core.py                               # 核心数据分类
└── adapters/                             # 数据源适配器
    └── customer_adapter.py               # Customer数据源
```

## 设计理念

1. **统一接口规范** - 使用`MyStocksUnifiedManager`隐藏底层数据库差异
2. **数据分类体系** - 基于数据特性的5大分类自动路由
3. **完整监控集成** - 所有操作自动记录到监控数据库
4. **配置驱动管理** - 通过外部配置文件管理参数
